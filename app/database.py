"""
Database engine and session management.

Uses sync SQLAlchemy 2.0 style for clarity and debuggability.
SQLite is the default (zero setup). Switch to PostgreSQL via DATABASE_URL env var.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# ── Engine ───────────────────────────────────────────────────────────────────

# SQLite needs check_same_thread=False for FastAPI's threaded request handling.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,  # Log SQL in debug mode
)

# Enable WAL mode and foreign keys for SQLite (performance + integrity)
if settings.DATABASE_URL.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ── Session Factory ──────────────────────────────────────────────────────────

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ── Base Model ───────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


def init_db():
    """Create all tables. Used for development and testing.
    
    In production, use Alembic migrations instead.
    """
    Base.metadata.create_all(bind=engine)
