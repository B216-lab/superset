# Superset Authentik SSO Specification

## Goal

Enable OAuth2/OpenID Connect SSO for Superset using Authentik so users can authenticate via the identity provider instead of local username/password login.

## Scope

- Configure Superset authentication mode to OAuth.
- Register Authentik as an OpenID Connect provider using discovery metadata.
- Add a custom security manager that maps Authentik user claims into Superset user fields.
- Configure role registration and example group-to-role mapping.

## Out of Scope

- Provisioning Authentik itself.
- Creating production secrets management.
- Enforcing environment-specific values.

## Configuration Requirements

### Authentication Mode

- `AUTH_TYPE = AUTH_OAUTH`
- `CUSTOM_SECURITY_MANAGER` points to a custom class implementing `oauth_user_info`.

### OAuth Provider

- A single provider named `authentik` in `OAUTH_PROVIDERS`.
- Use `server_metadata_url` for OIDC endpoint discovery.
- Include example placeholders for:
  - `client_id`
  - `client_secret`
  - `server_metadata_url`

### User Registration and Roles

- `AUTH_USER_REGISTRATION = True`
- `AUTH_USER_REGISTRATION_ROLE = "Gamma"` as the default least-privileged baseline.
- `AUTH_ROLES_MAPPING` with example Authentik group names to Superset roles.
- `AUTH_ROLES_SYNC_AT_LOGIN = True` to update memberships at each login.

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

- `AUTHENTIK_CLIENT_ID=<from Authentik>`
- `AUTHENTIK_CLIENT_SECRET=<from Authentik>`
- `AUTHENTIK_SERVER_METADATA_URL=<your .well-known/openid-configuration URL>`

### 4) Run Superset Locally

- Start stack: `docker compose up -d`
- Initialize metadata/users if needed: `docker compose run --rm superset-init`
- Open: `http://localhost:8088`
- Click **Sign in with authentik** and complete login.

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
- [ ] `docker/pythonpath_dev/superset_config.py` contains Authentik OAuth configuration and references the custom manager.
- [ ] `docker/pythonpath_dev/.gitignore` allows tracking `custom_sso_security_manager.py`.
