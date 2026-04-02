"""
Request ID middleware.

Assigns a unique UUID to every incoming request and includes it in the response
headers. This enables request tracing across logs — essential for debugging
in any production system.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attaches a unique X-Request-ID to every request/response cycle."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store on request state for access in route handlers and logs
        request.state.request_id = request_id

        # Process the request
        response: Response = await call_next(request)

        # Include request ID in response headers for client-side tracing
        response.headers["X-Request-ID"] = request_id

        return response
