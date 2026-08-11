# 📚 FastAPI Core Concepts & Implementation Guide

Welcome to your self-study implementation guide! This document breaks down every concept listed in your `README.md` roadmap with theoretical explanations, best practices, and copy-paste-ready code snippets.

---

## 📋 Table of Contents

1. [Path & Query Parameters (`Path`, `Query`)](#1-path--query-parameters-path-query)
2. [Request Body & Pydantic Schemas](#2-request-body--pydantic-schemas)
3. [Response Models & Data Filtering](#3-response-models--data-filtering)
4. [Dependency Injection (`Depends`) ⭐](#4-dependency-injection-depends-)
5. [APIRouter & Modular Architecture](#5-apirouter--modular-architecture)
6. [Error Handling & Status Codes](#6-error-handling--status-codes)
7. [Middleware & CORS](#7-middleware--cors)
8. [Background Tasks (`BackgroundTasks`)](#8-background-tasks-backgroundtasks)
9. [Testing with `TestClient` & `pytest`](#9-testing-with-testclient--pytest)
10. [Next Steps Roadmap](#10-next-steps-roadmap)

---

## 1. Path & Query Parameters (`Path`, `Query`)

### Concept

- **Path Parameters**: Part of the URL endpoint path (e.g. `/students/{student_id}`). Used for identifying specific resources. They are **mandatory**.
- **Query Parameters**: Key-value pairs after `?` in the URL (e.g. `/students?limit=10&age=18`). Used for filtering, pagination, and sorting. They can be **optional** or have default values.

### Advanced Validation with `Path()` and `Query()`

FastAPI provides `Path` and `Query` functions to add validation constraints, descriptions, and metadata directly in your route signatures.

```python
from fastapi import FastAPI, Path, Query
from typing import Optional

app = FastAPI()

@app.get("/students/{student_id}")
def get_student(
    # Path parameter validation
    student_id: int = Path(
        ...,
        ge=1000,
        le=9999,
        title="Student ID",
        description="Must be a 4-digit number between 1000 and 9999"
    ),
    # Query parameter validation
    age: Optional[int] = Query(
        None,
        ge=5,
        le=100,
        description="Filter by student age"
    ),
    search: str = Query(
        "",
        max_length=50,
        description="Search term for student name"
    )
):
    return {"student_id": student_id, "age": age, "search": search}
```

### Best Practices

- Use `Path()` for resource identifiers.
- Use `Query()` for search filters and pagination parameters.
- Always add `ge`, `le`, `min_length`, or `max_length` constraints to prevent invalid client inputs before your route logic executes.

---

## 2. Request Body & Pydantic Schemas

### Concept

A **Request Body** is data sent by the client to the API inside an HTTP `POST`, `PUT`, or `PATCH` request (usually formatted as JSON).

### Pydantic Models & Inheritance

Use Pydantic `BaseModel` to validate types, check required vs optional fields, and nest schemas.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional

app = FastAPI()

# 1. Nested Model
class Address(BaseModel):
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    zip_code: Optional[str] = Field(None, max_length=10)

# 2. Input Model (for receiving POST/PUT payloads)
class StudentIn(BaseModel):
    std_id: int = Field(..., ge=1000)
    std_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    dob: date
    address: Address

@app.post("/students")
def create_student(student: StudentIn):
    return {"message": "Student created", "data": student}
```

### Best Practices

- Use `EmailStr` from `pydantic` to validate email syntax automatically.
- Separate Input schemas (`StudentIn`) from Output schemas (`StudentOut`).

---

## 3. Response Models & Data Filtering

### Concept

The `response_model` parameter in FastAPI route decorators ensures that:

1. Output data is validated against a Pydantic schema.
2. Sensitive fields (like passwords or secret keys) are **filtered out** before sending the JSON response.
3. Interactive Swagger docs (`/docs`) accurately show the response data structure.

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

app = FastAPI()

# Response Schema (EXCLUDES password)
class StudentOut(BaseModel):
    std_id: int
    std_name: str
    email: EmailStr

@app.post("/register", response_model=StudentOut)
def register_student(student: StudentIn): # StudentIn contains password
    # FastAPI automatically filters out 'password' when returning
    return student
```

### Alternative: `exclude=True`

You can also set `exclude=True` directly on a Pydantic `Field`:

```python
class Credential(BaseModel):
    username: str
    password: str = Field(..., exclude=True) # Automatically hidden from JSON dumps
    email: EmailStr
```

### Best Practices

- **Never** return raw password strings or password hashes in API responses.
- Use `response_model=StudentOut` on GET, POST, and PUT endpoints to enforce consistent response structures.

---

## 4. Dependency Injection (`Depends`) ⭐

### Concept

**Dependency Injection** is a software design pattern where a function receives its dependencies from an external system rather than creating them internally.

In FastAPI, `Depends()` allows you to:

1. Share logic across multiple endpoints (e.g. authentication, query validation, rate limiting).
2. Manage database connections cleanly (opening & closing DB sessions automatically).

### Reusable Dependency Examples

#### Example A: Common Query Parameters

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# Shared dependency function
def pagination_params(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/students")
def get_students(pagination: dict = Depends(pagination_params)):
    return {"message": "Fetching students", "pagination": pagination}

@app.get("/courses")
def get_courses(pagination: dict = Depends(pagination_params)):
    return {"message": "Fetching courses", "pagination": pagination}
```

#### Example B: Database Session Placeholder (Preparation for SQLAlchemy)

```python
def get_db():
    db = "Fake Database Connection"
    try:
        yield db  # Provide the DB session to the route
    finally:
        print("Database connection closed") # Runs after the request finishes

@app.get("/data")
def read_data(db = Depends(get_db)):
    return {"db_status": db}
```

### Best Practices

- Use dependencies to keep route functions thin and focused on business logic.
- Use `yield` inside dependency functions for setup/teardown tasks (like closing DB sessions).

---

## 5. APIRouter & Modular Architecture

### Concept

As your application grows, keeping all code in a single `main.py` file becomes unmaintainable. `APIRouter` lets you break routes into modular feature files.

### Recommended Folder Structure

```text
student_app/
├── app/
│   ├── __init__.py
│   ├── main.py              # Creates FastAPI app & includes routers
│   ├── db.py                # Database connection/state
│   │
│   ├── schemas/             # Pydantic validation models
│   │   ├── __init__.py
│   │   └── student.py
│   │
│   └── routers/             # API route handlers
│       ├── __init__.py
│       ├── student_router.py
│       └── course_router.py
```

### Creating and Including a Router

**`app/routers/student_router.py`**:

```python
from fastapi import APIRouter, HTTPException, status
from typing import List

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("", response_model=List[str])
def list_students():
    return ["Alice", "Bob"]

@router.get("/{student_id}")
def get_student_by_id(student_id: int):
    return {"student_id": student_id}
```

**`app/main.py`**:

```python
from fastapi import FastAPI
from app.routers.student_router import router as student_router

app = FastAPI(title="Modular FastAPI App")

# Mount the router
app.include_router(student_router)
```

---

## 6. Error Handling & Status Codes

### Concept

Communicating errors clearly with appropriate HTTP status codes helps clients understand what went wrong.

### HTTP Status Code Guide

| Code  | Status Name           | When to Use                                        |
| :---- | :-------------------- | :------------------------------------------------- |
| `200` | OK                    | Successful GET, PUT, DELETE                        |
| `201` | Created               | Successful POST (resource created)                 |
| `204` | No Content            | Successful DELETE with no body returned            |
| `400` | Bad Request           | Client sent invalid data / business rule violation |
| `401` | Unauthorized          | Client is not logged in / missing auth token       |
| `403` | Forbidden             | Client is logged in but lacks permissions          |
| `404` | Not Found             | Requested resource ID does not exist               |
| `409` | Conflict              | Resource already exists (e.g. duplicate email/ID)  |
| `422` | Unprocessable Entity  | Pydantic type validation failure                   |
| `500` | Internal Server Error | Unhandled server crash / bug                       |

### Raising `HTTPException`

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID cannot be negative"
        )
    if item_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return {"item_id": item_id}
```

---

## 7. Middleware & CORS

### Concept

**Middleware** is a function that runs before every request is processed and after every response is returned.

### CORS Middleware (Cross-Origin Resource Sharing)

Frontend frameworks (React, Vue, Next.js) running on `http://localhost:3000` cannot talk to your backend on `http://localhost:8000` unless CORS is enabled.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"], # Allow GET, POST, PUT, DELETE, etc.
    allow_headers=["*"], # Allow all headers
)
```

### Custom Process-Time Middleware

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = call_next(request) # Execute route handler
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## 8. Background Tasks (`BackgroundTasks`)

### Concept

**Background Tasks** allow you to perform heavy or slow operations (sending emails, processing images, writing audit logs) **after** returning an HTTP response to the client immediately.

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_welcome_email(email: str, name: str):
    # Imagine this takes 3 seconds to send an email via SMTP
    print(f"Sending email to {name} ({email})...")

@app.post("/register")
def register(email: str, name: str, background_tasks: BackgroundTasks):
    # Add task to background execution queue
    background_tasks.add_task(send_welcome_email, email=email, name=name)

    # Client receives response IMMEDIATELY without waiting 3 seconds!
    return {"message": "Registration successful. Welcome email is being sent."}
```

---

## 9. Testing with `TestClient` & `pytest`

### Concept

Writing automated tests ensures that code modifications don't break existing API endpoints. FastAPI integrates with `httpx` and `pytest` using `TestClient`.

### Step 1: Install `pytest` and `httpx`

```bash
uv add --dev pytest httpx
```

### Step 2: Write Test File (`tests/test_main.py`)

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_get_invalid_student_id():
    response = client.get("/students/50") # ID < 1000
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Student ID. Student IDs must be 1000 or greater."
```

### Step 3: Run Pytest

```bash
uv run pytest
```

---

## 10. Next Steps Roadmap

Now that you have mastered FastAPI basics, here is your path forward to becoming a full-stack backend engineer:

```text
FastAPI Fundamentals (Done! 🎉)
       ↓
PostgreSQL & Relational DBs (Tables, Keys, Indexes)
       ↓
SQLAlchemy ORM & Alembic (Async DB Queries & Migrations)
       ↓
JWT Authentication & Password Hashing (OAuth2 + Passlib + PyJWT)
       ↓
Docker & Deployment (Dockerfiles, Uvicorn, Nginx/Render/Railway)
```
