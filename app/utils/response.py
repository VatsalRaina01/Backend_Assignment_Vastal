"""
Standardized API response helpers.

Every endpoint returns the same envelope shape — this makes frontend integration
predictable and debugging easier.
"""

from typing import Any


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: dict | None = None,
) -> dict:
    """Build a standardized success response.

    Args:
        data: The response payload.
        message: Human-readable success message.
        meta: Optional metadata (pagination info, etc.).

    Returns:
        Dict ready to be returned from a FastAPI endpoint.
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
    }
    if meta is not None:
        response["meta"] = meta
    return response


def paginated_response(
    data: list,
    total: int,
    page: int,
    limit: int,
    message: str = "Success",
) -> dict:
    """Build a paginated success response.

    Args:
        data: List of items for the current page.
        total: Total number of items across all pages.
        page: Current page number (1-indexed).
        limit: Items per page.
        message: Human-readable success message.

    Returns:
        Dict with data and pagination metadata.
    """
    total_pages = (total + limit - 1) // limit if limit > 0 else 0
    return success_response(
        data=data,
        message=message,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
    )
