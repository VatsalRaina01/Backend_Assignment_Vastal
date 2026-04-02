"""
Test fixtures — shared across all test files.

Sets up:
- In-memory SQLite test database (fast, isolated, disposable)
- Test client with proper auth helpers
- Pre-created users for each role

Each test gets a fresh database via function-scoped fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies import get_db
from app.main import app
from app.models.user import User, UserRole, UserStatus
from app.utils.security import create_access_token, hash_password


# ── Test Database Setup ──────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite://"  # In-memory SQLite

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # Reuse the same connection for in-memory DB
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="function")
def db():
    """Create all tables, yield a session, then tear down."""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client with DB dependency override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── User Factory Helpers ─────────────────────────────────────────────────────


def create_test_user(db, role: str = "viewer", email: str = None) -> User:
    """Create a test user with the given role."""
    if email is None:
        email = f"test_{role}@example.com"

    user = User(
        email=email,
        hashed_password=hash_password("testpassword123"),
        name=f"Test {role.title()}",
        role=UserRole(role),
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_auth_header(user: User) -> dict:
    """Generate an Authorization header for a test user."""
    token = create_access_token(subject=user.id, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


# ── Convenience Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def admin_user(db):
    """Create an admin user."""
    return create_test_user(db, role="admin")


@pytest.fixture
def analyst_user(db):
    """Create an analyst user."""
    return create_test_user(db, role="analyst")


@pytest.fixture
def viewer_user(db):
    """Create a viewer user."""
    return create_test_user(db, role="viewer")


@pytest.fixture
def admin_headers(admin_user):
    """Auth headers for admin user."""
    return get_auth_header(admin_user)


@pytest.fixture
def analyst_headers(analyst_user):
    """Auth headers for analyst user."""
    return get_auth_header(analyst_user)


@pytest.fixture
def viewer_headers(viewer_user):
    """Auth headers for viewer user."""
    return get_auth_header(viewer_user)
