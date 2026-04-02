"""
FastAPI application factory.

Assembles the full application:
- Middleware (CORS, request ID, rate limiting)
- Exception handlers (app errors, validation, generic)
- Router registration
- Health check
- Swagger/OpenAPI configuration
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.database import init_db
from app.middleware.request_id import RequestIDMiddleware
from app.routers import auth, dashboard, records, users
from app.utils.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.utils.exceptions import AppException

# ── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Rate Limiter ─────────────────────────────────────────────────────────────

limiter = Limiter(key_func=get_remote_address)


# ── Lifespan ─────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    # Startup
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database initialized.")
    logger.info(
        "%s v%s is running! Docs at http://localhost:8000/docs",
        settings.APP_NAME,
        settings.APP_VERSION,
    )
    yield
    # Shutdown
    logger.info("Shutting down...")


# ── App Creation ─────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "A finance dashboard backend API with role-based access control, "
            "financial record management, and analytics endpoints.\n\n"
            "## Authentication\n"
            "All protected endpoints require a JWT token in the "
            "`Authorization: Bearer <token>` header.\n\n"
            "## Roles\n"
            "- **Viewer**: Can view financial records\n"
            "- **Analyst**: Can view records + access dashboard analytics\n"
            "- **Admin**: Full access — CRUD records and manage users\n\n"
            "## Quick Start\n"
            "1. Register or login to get a token\n"
            "2. Click the 🔒 **Authorize** button above and enter your token\n"
            "3. Try out the endpoints!"
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Middleware ────────────────────────────────────────────────────────
    # Order matters: outermost first

    # CORS — allow all origins for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID for log correlation
    app.add_middleware(RequestIDMiddleware)

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Exception Handlers ───────────────────────────────────────────────

    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # ── Routers ──────────────────────────────────────────────────────────

    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(records.router)
    app.include_router(dashboard.router)

    # ── Health Check ─────────────────────────────────────────────────────

    @app.get("/health", tags=["System"], summary="Health check")
    def health_check():
        """Check if the API is running and the database is accessible."""
        from sqlalchemy import text
        from app.database import SessionLocal

        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_status = "connected"
        except Exception:
            db_status = "disconnected"

        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "database": db_status,
        }

    # ── Root Endpoint ────────────────────────────────────────────────────

    @app.get("/", tags=["System"], summary="API root")
    def root():
        """Welcome endpoint with links to documentation."""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }

    return app


# Create the app instance — used by uvicorn
app = create_app()
