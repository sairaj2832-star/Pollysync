from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)


if settings.database_url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def set_sqlite_pragmas(dbapi_connection, _) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.models  # noqa: F401

    settings.validate_security()
    Base.metadata.create_all(bind=engine)
    reconcile_sqlite_schema()


def reconcile_sqlite_schema() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    with engine.begin() as connection:
        if "users" in table_names:
            existing_columns = {column["name"] for column in inspector.get_columns("users")}
            user_migrations = {
                "oauth_provider": "ALTER TABLE users ADD COLUMN oauth_provider VARCHAR(50)",
                "oauth_subject": "ALTER TABLE users ADD COLUMN oauth_subject VARCHAR(255)",
                "is_active": "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL",
                "phone": "ALTER TABLE users ADD COLUMN phone VARCHAR(30)",
                "role": "ALTER TABLE users ADD COLUMN role VARCHAR(80)",
                "organization": "ALTER TABLE users ADD COLUMN organization VARCHAR(255)",
                "language": "ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'en'",
            }
            for column_name, statement in user_migrations.items():
                if column_name not in existing_columns:
                    connection.execute(text(statement))

        if "farms" in table_names:
            existing_columns = {column["name"] for column in inspector.get_columns("farms")}
            farm_migrations = {
                "location_name": "ALTER TABLE farms ADD COLUMN location_name VARCHAR(255)",
                "area_acres": "ALTER TABLE farms ADD COLUMN area_acres FLOAT",
                "soil_type": "ALTER TABLE farms ADD COLUMN soil_type VARCHAR(50)",
                "user_id": "ALTER TABLE farms ADD COLUMN user_id INTEGER",
                "variety": "ALTER TABLE farms ADD COLUMN variety VARCHAR(80)",
                "irrigation_method": "ALTER TABLE farms ADD COLUMN irrigation_method VARCHAR(50)",
                "planting_date": "ALTER TABLE farms ADD COLUMN planting_date VARCHAR(16)",
                "harvest_date": "ALTER TABLE farms ADD COLUMN harvest_date VARCHAR(16)",
            }
            for column_name, statement in farm_migrations.items():
                if column_name not in existing_columns:
                    connection.execute(text(statement))

            nullable_location_migrations = {
                "location_lat": "UPDATE farms SET location_lat = NULL WHERE location_lat = ''",
                "location_lng": "UPDATE farms SET location_lng = NULL WHERE location_lng = ''",
            }
            for column_name, statement in nullable_location_migrations.items():
                if column_name in existing_columns:
                    connection.execute(text(statement))
