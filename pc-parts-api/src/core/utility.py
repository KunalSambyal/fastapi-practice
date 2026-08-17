from typing import Any
from fastapi import Request
from fastapi.responses import JSONResponse


class ApiResponse(JSONResponse):
    """Custom JSONResponse subclass ensuring standard header and status formatting."""

    pass


async def get_request_data(content_type: str, request: Request) -> dict[str, Any]:
    """Extracts payload data from JSON bodies, URL query parameters, or form data."""
    if "application/json" in content_type:
        try:
            return await request.json()
        except Exception:
            return {}
    elif request.query_params:
        return dict(request.query_params)
    return {}
