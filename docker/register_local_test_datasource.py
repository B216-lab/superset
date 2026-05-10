from __future__ import annotations

import logging
import os

from superset.app import create_app

logger = logging.getLogger(__name__)


def _build_sqlalchemy_uri() -> str:
    """Build SQLAlchemy URI for disposable local test database."""
    user = os.getenv("LOCAL_TEST_DB_USER", "superset_test")
    password = os.getenv("LOCAL_TEST_DB_PASSWORD", "superset_test")
    host = os.getenv("LOCAL_TEST_DB_HOST", "superset_test_db")
    port = os.getenv("LOCAL_TEST_DB_PORT", "5432")
    database = os.getenv("LOCAL_TEST_DB_NAME", "superset_test")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def main() -> None:
    """Register or update local disposable datasource in Superset metadata DB."""
    app = create_app()
    app.app_context().push()

    from superset import db
    from superset.models.core import Database

    database_name = os.getenv("LOCAL_TEST_DATASOURCE_NAME", "Local Test Postgres")
    sqlalchemy_uri = _build_sqlalchemy_uri()

    database = (
        db.session.query(Database).filter_by(database_name=database_name).one_or_none()
    )
    if database is None:
        database = Database(
            database_name=database_name,
            expose_in_sqllab=True,
            allow_ctas=True,
            allow_cvas=True,
            allow_dml=False,
        )
        db.session.add(database)

    database.set_sqlalchemy_uri(sqlalchemy_uri)
    db.session.commit()

    with database.get_sqla_engine() as engine:
        with engine.connect():
            pass

    logger.info("Registered local test datasource '%s'", database_name)


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("SUPERSET_LOG_LEVEL", "INFO").upper())
    main()
