from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: str
    message: str
    code: int
    data: T | None = None

    @classmethod
    def success(
        cls, data: Any = None, message: str = "Success", code: int = 200
    ) -> "APIResponse[Any]":
        return cls(status="success", message=message, code=code, data=data)

    @classmethod
    def error(
        cls, message: str = "Error", code: int = 400, data: Any = None
    ) -> "APIResponse[Any]":
        return cls(status="error", message=message, code=code, data=data)
