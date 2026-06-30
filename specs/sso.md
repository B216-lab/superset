# Superset Authentik SSO Specification

## Goal

Enable OAuth2/OpenID Connect SSO for Superset using Authentik in normal mode, while keeping a local development mode that can use Superset username/password login without Authentik.

### Authentication Mode

- `SUPERSET_AUTH_MODE` environment variable controls auth mode.
- Supported values:
  - `oauth` -> `AUTH_TYPE = AUTH_OAUTH`
  - `db` -> `AUTH_TYPE = AUTH_DB`
- `CUSTOM_SECURITY_MANAGER` points to a custom class implementing `oauth_user_info` only in OAuth mode.
- Invalid auth mode values must fail fast with a clear error.

### OAuth Provider

- A single provider named `authentik` in `OAUTH_PROVIDERS`.
- Build `server_metadata_url` from Authentik base URL and application slug.
- Include example placeholders for:
  - `base_url`
  - `application_slug`
  - `client_id`
  - `client_secret`
- OAuth mode must validate required Authentik environment variables and fail fast if they are missing.

### User Registration and Roles

- `AUTH_USER_REGISTRATION = True`
- `AUTH_USER_REGISTRATION_ROLE = "Gamma"` as the default least-privileged baseline.
- `AUTH_ROLES_MAPPING` with example Authentik group names to Superset roles.
- `AUTH_ROLES_SYNC_AT_LOGIN = True` to update memberships at each login.

### Local Development Mode

- Local development mode uses Superset database authentication.
- Existing init flow admin user (`admin` / `${ADMIN_PASSWORD:-admin}`) must be able to log in when `SUPERSET_AUTH_MODE=db`.
- Local development override/profile should set:
  - `SUPERSET_AUTH_MODE=db`
  - `SUPERSET_LOG_LEVEL=debug`
  - `FLASK_DEBUG=true`
  - `SUPERSET_ENV=development`
- Local development override/profile should also:
  - start a disposable PostgreSQL datasource container with seeded sample rows
  - register that datasource in Superset during init
  - load Superset example dashboards/charts for faster UI testing
- Local development instructions must explain how to start stack without Authentik via Just recipe.
- Just recipe must write local override env file so `superset-init` starts in DB auth mode even when base `.env` defaults to OAuth.

### Claim Mapping

The custom security manager maps standard OIDC claims from Authentik userinfo:

- `preferred_username` -> `username`
- `name` -> `name`
- `email` -> `email`
- `given_name` -> `first_name`
- `family_name` -> `last_name`
- `groups` -> `role_keys`

## Operational Notes

- Superset OAuth callback URL pattern:
  - `https://<superset-host>/oauth-authorized/authentik`
- This exact callback must be configured in the Authentik application/provider.
- Placeholder values must be replaced before real deployment.

## Local Authentik Setup and Superset Test

Use this checklist to finish setup and verify SSO locally with Docker Compose.

### 1) Configure Authentik Provider and Application

In Authentik admin:

- Create an **OAuth2/OpenID Provider** (authorization code flow).
- Set redirect URI to local Superset callback:
  - `http://localhost:8088/oauth-authorized/authentik`
- Ensure scopes include:
  - `openid`
  - `profile`
  - `email`
- Save and note:
  - client ID
  - client secret
- Create an **Application** and attach it to this provider.
- Note the issuer/discovery URL. For this project, it should match:
  - `https://<authentik-host>/application/o/<provider-slug>/.well-known/openid-configuration`

### 2) Create Authentik Groups for Superset Role Mapping

Create groups in Authentik matching `AUTH_ROLES_MAPPING` keys:

- `superset_admins`
- `superset_alpha`
- `superset_gamma`

Assign your test user to at least one group.

### 3) Configure Local Secrets in Superset

Set values in `docker/.env-local` (keep this file untracked):

- `SUPERSET_AUTH_MODE=oauth`
- `AUTHENTIK_BASE_URL=<your Authentik base URL>`
- `AUTHENTIK_APPLICATION_SLUG=<your provider slug>`
- `AUTHENTIK_CLIENT_ID=<from Authentik>`
- `AUTHENTIK_CLIENT_SECRET=<from Authentik>`
