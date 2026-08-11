from fastapi import status, HTTPException, APIRouter
from typing import List
from app.schemas.student import StudentOut, StudentIn
from app.db import students

router = APIRouter(tags=["Students"])


# 127.0.0.1:8000/search?name=Kunal+s&id=2
# {"name":"Kunal s","id":2}
@router.get("/search")
def search_student(name: str, id: int):
    return {"name": name, "id": id}


@router.get("/students", response_model=List[StudentOut])
def get_students():
    return students


@router.get("/students/{id}", response_model=StudentOut)
def get_student(id: int):
    if id < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Student ID. Student IDs must be 1000 or greater.",
        )
    for student in students:
        if student.std_id == id:
            return student
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
    )


@router.post(
    "/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED
)
def register_student(student: StudentIn):
    for existing_student in students:
        if existing_student.std_id == student.std_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Student already exists"
            )
    students.append(student)
    return student


@router.put("/students/{id}", response_model=StudentOut)
def update_student(id: int, new_student: StudentIn):
    if id < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Student ID. Student IDs must be 1000 or greater.",
        )
    if new_student.std_id != id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path ID and Student ID in payload do not match.",
        )
    for idx, student in enumerate(students):
        if student.std_id == id:
            students[idx] = new_student
            return new_student
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
    )


@router.delete("/students/{id}", response_model=StudentOut)
def delete_student(id: int):
    if id < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Student ID. Student IDs must be 1000 or greater.",
        )
    for idx, student in enumerate(students):
        if student.std_id == id:
            students.pop(idx)
            return student
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
    )
