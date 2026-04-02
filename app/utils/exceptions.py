"""
Custom exception classes for the application.

Each maps to a specific HTTP status code and provides structured error info.
These are caught by global exception handlers (see exception_handlers.py).
"""


class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: dict | list | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str = "Resource", identifier: str = ""):
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=detail,
            status_code=404,
            error_code="NOT_FOUND",
        )


class UnauthorizedException(AppException):
    """Authentication failed (401)."""

    def __init__(self, message: str = "Invalid or expired authentication credentials"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """Insufficient permissions (403)."""

    def __init__(self, message: str = "You do not have permission to perform this action"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class ConflictException(AppException):
    """Resource conflict, e.g. duplicate email (409)."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
        )


class BadRequestException(AppException):
    """Invalid request data (400)."""

    def __init__(self, message: str = "Invalid request", details: dict | list | None = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BAD_REQUEST",
            details=details,
        )
