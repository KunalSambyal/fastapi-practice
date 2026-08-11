from fastapi import Path, Query, APIRouter
from typing import Optional

router = APIRouter()


@router.get("/students/{id}")
def get_student(
    id: int = Path(
        ...,
        ge=1000,
        le=9999,
        title="Student ID",
        description="Must be a 4-digit number between 1000 and 9999",
    ),
    age: Optional[int] = Query(None, ge=5, le=100, description="Filter by student age"),
    search: str = Query("", max_length=50, description="Search term for student name"),
):
    return {"std_id": id, "age": age, "search": search}


