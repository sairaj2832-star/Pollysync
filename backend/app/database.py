from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Determine if we're using PostgreSQL (Supabase) or SQLite
is_postgresql = settings.database_url.startswith("postgresql")

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_size=10 if is_postgresql else 5,
    max_overflow=20 if is_postgresql else 10,
)


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
    
    if not is_postgresql:
        reconcile_sqlite_schema()
    
    # Seed districts for both SQLite and PostgreSQL
    seed_districts_if_needed()


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


def seed_districts_if_needed() -> None:
    """Seed Maharashtra districts if they don't exist."""
    from app.models.farm import District
    
    with SessionLocal() as session:
        # Check if districts exist
        existing_count = session.query(District).count()
        if existing_count > 0:
            return
        
        # Seed Maharashtra districts
        districts = [
            District(slug="amaravati", name="Amaravati", state="Maharashtra", centroid_lat=16.2348, centroid_lng=79.7433, radius_km=5.0),
            District(slug="aurangabad", name="Aurangabad", state="Maharashtra", centroid_lat=19.8762, centroid_lng=75.3433, radius_km=5.0),
            District(slug="jalgaon", name="Jalgaon", state="Maharashtra", centroid_lat=21.0078, centroid_lng=75.9928, radius_km=5.0),
            District(slug="kolhapur", name="Kolhapur", state="Maharashtra", centroid_lat=16.7050, centroid_lng=74.2433, radius_km=5.0),
            District(slug="latur", name="Latur", state="Maharashtra", centroid_lat=18.4088, centroid_lng=76.5602, radius_km=5.0),
            District(slug="nagpur", name="Nagpur", state="Maharashtra", centroid_lat=21.1458, centroid_lng=79.0882, radius_km=5.0),
            District(slug="nashik", name="Nashik", state="Maharashtra", centroid_lat=19.9975, centroid_lng=73.7898, radius_km=5.0),
            District(slug="pune", name="Pune", state="Maharashtra", centroid_lat=18.5204, centroid_lng=73.8567, radius_km=5.0),
            District(slug="satara", name="Satara", state="Maharashtra", centroid_lat=17.6868, centroid_lng=73.9997, radius_km=5.0),
            District(slug="solapur", name="Solapur", state="Maharashtra", centroid_lat=17.6599, centroid_lng=75.9064, radius_km=5.0),
            District(slug="mumbai", name="Mumbai", state="Maharashtra", centroid_lat=19.0760, centroid_lng=72.8777, radius_km=5.0),
            District(slug="ahmednagar", name="Ahmednagar", state="Maharashtra", centroid_lat=19.0952, centroid_lng=74.7496, radius_km=5.0),
            District(slug="amravati", name="Amravati", state="Maharashtra", centroid_lat=20.9374, centroid_lng=77.7796, radius_km=5.0),
            District(slug="chandrapur", name="Chandrapur", state="Maharashtra", centroid_lat=19.9615, centroid_lng=79.3032, radius_km=5.0),
            District(slug="dhule", name="Dhule", state="Maharashtra", centroid_lat=20.9040, centroid_lng=74.7748, radius_km=5.0),
            District(slug="gadchiroli", name="Gadchiroli", state="Maharashtra", centroid_lat=20.1809, centroid_lng=80.0883, radius_km=5.0),
            District(slug="gondia", name="Gondia", state="Maharashtra", centroid_lat=21.4602, centroid_lng=80.1883, radius_km=5.0),
            District(slug="hingoli", name="Hingoli", state="Maharashtra", centroid_lat=19.7150, centroid_lng=77.1310, radius_km=5.0),
            District(slug="nanded", name="Nanded", state="Maharashtra", centroid_lat=19.1388, centroid_lng=77.3218, radius_km=5.0),
            District(slug="parbhani", name="Parbhani", state="Maharashtra", centroid_lat=19.2686, centroid_lng=76.7708, radius_km=5.0),
            District(slug="wardha", name="Wardha", state="Maharashtra", centroid_lat=20.7453, centroid_lng=78.6023, radius_km=5.0),
            District(slug="washim", name="Washim", state="Maharashtra", centroid_lat=20.1117, centroid_lng=77.1330, radius_km=5.0),
            District(slug="yavatmal", name="Yavatmal", state="Maharashtra", centroid_lat=20.3897, centroid_lng=78.1308, radius_km=5.0),
        ]
        
        session.add_all(districts)
        session.commit()
