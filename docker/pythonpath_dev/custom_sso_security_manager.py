from __future__ import annotations

from typing import Any

from superset.security import SupersetSecurityManager


class CustomSsoSecurityManager(SupersetSecurityManager):
    """Map Authentik OAuth user claims to Superset user fields."""

    def oauth_user_info(
        self, provider: str, response: Any | None = None
    ) -> dict[str, Any]:
        """Return normalized user attributes for the configured OAuth provider.

        Args:
            provider: OAuth provider name from OAUTH_PROVIDERS.
            response: Optional OAuth response object from FAB.

        Returns:
            Dictionary of fields used by FAB/Superset user provisioning.
        """
        if provider != "authentik":
            return {}

        userinfo = self.appbuilder.sm.oauth_remotes[provider].get("userinfo/").json()

        return {
            "username": userinfo.get("preferred_username"),
            "name": userinfo.get("name"),
            "email": userinfo.get("email"),
            "first_name": userinfo.get("given_name", ""),
            "last_name": userinfo.get("family_name", ""),
            "role_keys": userinfo.get("groups", []),
        }
