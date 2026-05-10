import logging
import os
import sys

from celery.schedules import crontab
from custom_sso_security_manager import CustomSsoSecurityManager
from flask_appbuilder.security.manager import AUTH_DB, AUTH_OAUTH
from flask_caching.backends.filesystemcache import FileSystemCache
from redis import Redis

logger = logging.getLogger()

DATABASE_DIALECT = os.getenv("DATABASE_DIALECT")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_DB = os.getenv("DATABASE_DB")

TALISMAN_ENABLED = False

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"{DATABASE_USER}:{DATABASE_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_DB}"
)

BABEL_DEFAULT_LOCALE = "ru"

LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "ru": {"flag": "ru", "name": "Русский"},
}
PUBLIC_ROLE_LIKE = "Gamma"
AUTH_ROLE_PUBLIC = "Public"

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

SESSION_SERVER_SIDE = True
SESSION_TYPE = "redis"
SESSION_REDIS = Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=int(REDIS_CELERY_DB))
SESSION_USE_SIGNER = True

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {"ALERT_REPORTS": True, "DASHBOARD_RBAC": True}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = f"http://superset_app{os.environ.get('SUPERSET_APP_ROOT', '/')}/"  # When using docker compose baseurl should be http://superset_nginx{ENV{BASEPATH}}/  # noqa: E501
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = (
    f"http://localhost:8888/{os.environ.get('SUPERSET_APP_ROOT', '/')}/"
)
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)


def _get_auth_mode() -> str:
    auth_mode = os.getenv("SUPERSET_AUTH_MODE", "oauth").strip().lower()
    allowed_modes = {"db", "oauth"}
    if auth_mode not in allowed_modes:
        allowed_modes_text = ", ".join(sorted(allowed_modes))
        raise ValueError(
            "Unsupported SUPERSET_AUTH_MODE="
            f"{auth_mode!r}. Expected one of: {allowed_modes_text}."
        )
    return auth_mode


if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

SUPERSET_AUTH_MODE = _get_auth_mode()
AUTH_TYPE = AUTH_DB

if SUPERSET_AUTH_MODE == "oauth":
    # CHANGEME: set these values in docker/.env-local before deployment.
    authentik_settings = {
        "AUTHENTIK_CLIENT_ID": os.getenv("AUTHENTIK_CLIENT_ID"),
        "AUTHENTIK_CLIENT_SECRET": os.getenv("AUTHENTIK_CLIENT_SECRET"),
        "AUTHENTIK_BASE_URL": os.getenv("AUTHENTIK_BASE_URL"),
        "AUTHENTIK_APPLICATION_SLUG": os.getenv("AUTHENTIK_APPLICATION_SLUG"),
    }
    missing_authentik_settings = [
        key for key, value in authentik_settings.items() if not value
    ]
    if missing_authentik_settings:
        missing_authentik_settings_text = ", ".join(missing_authentik_settings)
        raise ValueError(
            "SUPERSET_AUTH_MODE='oauth' requires Authentik settings: "
            f"{missing_authentik_settings_text}."
        )

    authentik_base_url = authentik_settings["AUTHENTIK_BASE_URL"]
    authentik_application_slug = authentik_settings["AUTHENTIK_APPLICATION_SLUG"]
    authentik_app_base_url = (
        f"{authentik_base_url}/application/o/{authentik_application_slug}/"
    )

    AUTH_TYPE = AUTH_OAUTH
    AUTH_USER_REGISTRATION = True
    AUTH_USER_REGISTRATION_ROLE = "Gamma"
    AUTH_ROLES_SYNC_AT_LOGIN = True
    AUTH_ROLES_MAPPING = {
        "superset_admins": ["Admin"],
        "superset_alpha": ["Alpha"],
        "superset_gamma": ["Gamma"],
    }
    OAUTH_PROVIDERS = [
        {
            "name": "authentik",
            "token_key": "access_token",
            "icon": "fa-lock",
            "remote_app": {
                "api_base_url": authentik_app_base_url,
                "client_id": authentik_settings["AUTHENTIK_CLIENT_ID"],
                "client_secret": authentik_settings["AUTHENTIK_CLIENT_SECRET"],
                "server_metadata_url": (
                    f"{authentik_app_base_url}.well-known/openid-configuration"
                ),
                "client_kwargs": {
                    "scope": "openid profile email",
                    "token_endpoint_auth_method": "client_secret_basic",
                },
                "access_token_url": f"{authentik_base_url}/application/o/token/",
                "authorize_url": f"{authentik_base_url}/application/o/authorize/",
            },
        }
    ]
    CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

logger.info("Superset auth mode: %s", SUPERSET_AUTH_MODE)
ENABLE_PROXY_FIX = True
#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
    )
except ImportError:
    logger.info("Using default Docker config...")
