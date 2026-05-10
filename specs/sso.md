# Superset Authentik SSO Specification

## Goal

Enable OAuth2/OpenID Connect SSO for Superset using Authentik in normal mode, while keeping a local development mode that can use Superset username/password login without Authentik.

## Scope

- Configure Superset authentication mode to OAuth.
- Allow switching authentication mode by environment for local development.
- Register Authentik as an OpenID Connect provider using discovery metadata.
- Add a custom security manager that maps Authentik user claims into Superset user fields.
- Configure role registration and example group-to-role mapping.
- Provide a local Docker Compose override/profile with debug-friendly logging and local DB auth.
- Provide a local Docker Compose override/profile with a disposable test datasource and sample content for dashboard/chart testing.

## Out of Scope

- Provisioning Authentik itself.
- Creating production secrets management.
- Enforcing environment-specific values.

## Configuration Requirements

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

### 4) Run Superset Locally With Authentik

- Start stack: `docker compose up -d`
- Initialize metadata/users if needed: `docker compose run --rm superset-init`
- Open: `http://localhost:8088`
- Click **Sign in with authentik** and complete login.

### 4a) Run Superset Locally Without Authentik

- Start local dev stack: `just local-dev`
- Open: `http://localhost:8088`
- Log in with local admin user:
  - username: `admin`
  - password: `${ADMIN_PASSWORD:-admin}`
- Validate local test datasource exists in Superset:
  - database name: `Local Test Postgres`
  - seeded table: `public.sales_orders`
- Validate example dashboards/charts were loaded for quick smoke testing.

### 5) Validate Role Assignment

After first login:

- Open Superset admin user list as an existing admin user.
- Confirm the new OAuth user exists.
- Confirm mapped roles match Authentik group membership.
- If role permissions look stale, re-run: `docker compose exec superset_app superset init`

## Superset Built-in Roles

### Admin

- Full administrative access.
- Can manage users, roles, permissions, connections, dashboards, and security settings.

### Alpha

- Power-user/creator role.
- Can create and edit charts/dashboards and work broadly with data sources.
- Cannot administer platform security like an Admin.

### Gamma

- Restricted consumer role.
- Intended for users with limited access to explicitly granted datasets/dashboards.
- Good default registration role when using SSO.

## Completion Criteria

- [ ] A tracked spec exists at `specs/sso.md`.
- [ ] A tracked custom security manager exists in `docker/pythonpath_dev/custom_sso_security_manager.py`.
- [ ] `docker/pythonpath_dev/superset_config.py` supports `oauth` and `db` auth modes via environment variable.
- [ ] `docker/pythonpath_dev/superset_config.py` contains Authentik OAuth configuration and references the custom manager only in OAuth mode.
- [ ] A tracked local Compose override/profile exists for development mode without Authentik.
- [ ] Local development profile starts a seeded disposable datasource container and registers it in Superset.
- [ ] Local development profile loads Superset example dashboards/charts.
- [ ] Local development docs explain how to log in without Authentik and reference Just recipe.
- [ ] `docker/pythonpath_dev/.gitignore` allows tracking `custom_sso_security_manager.py`.
