from typing import Any
from fastapi import Request
from src.core.utility import ApiResponse, get_request_data
from src.schemas.response_schema import APIResponse
from src.services.cpu_service import CpuService


async def cpu_controller(
    request: Request,
    auth_data: dict[str, Any] | None = None,
) -> ApiResponse:
    """Dispatches HTTP requests to CpuService and envelopes responses."""
    data = await get_request_data(request.headers.get("content-type", ""), request)

    method = request.method

    match method:
        case "POST":
            result, status_code = await CpuService.save(**data)
            message = "CPU created or updated successfully"

        case "GET":
            result, status_code = await CpuService.filter(**data)
            message = "CPUs retrieved successfully"

        case "PUT":
            result, status_code = await CpuService.update(**data)
            message = "CPU updated successfully"

        case "DELETE":
            result, status_code = await CpuService.delete(**data)
            message = "CPU deleted successfully"

        case _:
            return ApiResponse(
                content={
                    "status": "error",
                    "message": "Method not allowed",
                    "code": 405,
                    "data": None,
                },
                status_code=405,
            )

    if status_code >= 400:
        err_msg = (
            result.get("error", "An error occurred")
            if isinstance(result, dict)
            else message
        )
        response_data = APIResponse.error(message=err_msg, code=status_code)
    else:
        response_data = APIResponse.success(
            data=result, message=message, code=status_code
        )

    return ApiResponse(content=response_data.model_dump(), status_code=status_code)
