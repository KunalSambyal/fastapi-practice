# FastAPI Study Guide

Welcome to the comprehensive FastAPI guide. This README covers all the theoretical definitions, core concepts, practical code snippets, project structure, and modern workflow tools like `uv` to go from beginner to confident REST API developer.

---

## Table of Contents

1. [Core Concepts & Definitions](#1-core-concepts--definitions)
2. [Environment Setup & Installation (pip & uv)](#2-environment-setup--installation-pip--uv)
3. [Your First FastAPI Application](#3-your-first-fastapi-application)
4. [HTTP Methods](#4-http-methods)
5. [Path vs. Query Parameters](#5-path-vs-query-parameters)
6. [Data Validation with Pydantic](#6-data-validation-with-pydantic)
7. [Complete In-Memory CRUD API Example](#7-complete-in-memory-crud-api-example)
8. [HTTP Status Codes & Exception Handling](#8-http-status-codes--exception-handling)
9. [Response Models](#9-response-models)
10. [Bonus Concepts: Folder Structure (Standard & `uv`) & Dependency Injection](#10-bonus-concepts-folder-structure-standard--uv--dependency-injection)

---

## 1. Core Concepts & Definitions

### What is an API?

**API** stands for _Application Programming Interface_. It is a set of rules and protocols that allows different software applications to communicate with each other over the network. In web development, APIs usually accept HTTP requests and return responses (often in JSON format).

### What is REST?

**REST** stands for _Representational State Transfer_. It is an architectural style for designing networked applications. A **RESTful API** uses HTTP standard methods (GET, POST, PUT, DELETE) to manipulate resources identified by URLs. Key principles of REST include:

- **Statelessness**: Every request contains all the information needed to understand and process it.
- **Resource-based URLs**: Endpoints represent resources (e.g., `/students`, `/books/10`).
- **Standard HTTP Verbs**: Standardized actions performed on resources.

### Why FastAPI?

[FastAPI](https://fastapi.tiangolo.com/) is a modern, high-performance web framework for building APIs with Python 3.8+ based on standard Python type hints.

- **High Performance**: Powered by Starlette and Pydantic, matching Node.js and Go in speed.
- **Fast to Code**: Type hints enable autocomplete, reducing bugs significantly.
- **Auto-Generated Documentation**: Generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) automatically.
- **Automatic Validation**: Validates incoming data using Pydantic out of the box.

### FastAPI vs. Flask (High-Level Comparison)

| Feature               | Flask                                    | FastAPI                              |
| :-------------------- | :--------------------------------------- | :----------------------------------- |
| **Execution Model**   | Synchronous (WSGI) by default            | Asynchronous (ASGI) native support   |
| **Data Validation**   | Manual / Third-party (e.g., Marshmallow) | Automatic using Pydantic models      |
| **API Documentation** | Manual or third-party extensions         | Built-in automatic OpenAPI / Swagger |
| **Type Safety**       | Optional, not deeply integrated          | Built into the framework core        |

---

## 2. Environment Setup & Installation (pip & uv)

### Option A: Standard Setup (`venv` + `pip`)

#### Step 1: Create a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 2: Install FastAPI & Uvicorn

FastAPI requires an **ASGI server** to run. [Uvicorn](https://www.uvicorn.org/) is the standard lightning-fast ASGI server.

```bash
pip install fastapi uvicorn
```

#### Step 3: Run the Server

```bash
uvicorn main:app --reload
```

---

### Option B: Modern Setup using `uv` (Recommended ⚡)

[`uv`](https://docs.astral.sh/uv/) is an extremely fast Python package and project manager written in Rust by Astral (creators of Ruff). It replaces `pip`, `pip-tools`, `virtualenv`, and `poetry`.

#### Step 1: Initialize a Project with `uv init`

```bash
# Initialize a new project in the current directory
uv init

# Or create a new application directory
uv init my-fastapi-app
cd my-fastapi-app
```

`uv init` generates:

- `pyproject.toml`: Project configuration & dependencies definition.
- `.python-version`: Pins the Python version for the project.
- `.gitignore`: Standard Python gitignore rules.
- `README.md` & `main.py` / `hello.py`: Boilerplate project files.

#### Step 2: Add Dependencies with `uv add`

```bash
uv add fastapi uvicorn
```

`uv` automatically creates a `.venv` virtual environment if one doesn't exist, updates `pyproject.toml`, and creates a deterministic `uv.lock` file.

#### Step 3: Run the Server with `uv run`

```bash
uv run uvicorn main:app --reload
```

`uv run` ensures the command runs in the project's virtual environment automatically without manually activating `.venv`.

---

## 3. Your First FastAPI Application

Create a file named `main.py`:

```python
from fastapi import FastAPI

# 1. Create a FastAPI instance
app = FastAPI(
    title="My First FastAPI App",
    description="Getting started with FastAPI",
    version="1.0.0"
)

# 2. Define a path operation (decorator + function)
@app.get("/")
def read_root():
    return {"message": "Hello, World!", "status": "active"}
```

### Interactive API Documentation

FastAPI automatically generates interactive documentation for your endpoints:

- **Swagger UI**: Visit `http://127.0.0.1:8000/docs` in your browser. You can test endpoints directly from here!
- **ReDoc**: Visit `http://127.0.0.1:8000/redoc` for clean, alternative documentation.

---

## 4. HTTP Methods

HTTP methods specify the desired action to be performed on a resource:

| Method       | CRUD Action | Purpose                                 | Example                      |
| :----------- | :---------- | :-------------------------------------- | :--------------------------- |
| **`GET`**    | Read        | Retrieve data from the server           | Fetching a student's details |
| **`POST`**   | Create      | Send data to create a new resource      | Adding a new student         |
| **`PUT`**    | Update      | Replace an existing resource completely | Updating student information |
| **`DELETE`** | Delete      | Remove a resource                       | Deleting a student record    |

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def get_items():
    return {"action": "Fetch all items"}

@app.post("/items")
def create_item():
    return {"action": "Create a new item"}

@app.put("/items/{item_id}")
def update_item(item_id: int):
    return {"action": f"Update item {item_id}"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return {"action": f"Delete item {item_id}"}
```

---

## 5. Path vs. Query Parameters

### Path Parameters

Path parameters are embedded directly within the URL path. They are mandatory and typically used to identify a specific resource.

```python
@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    # FastAPI automatically parses user_id to an integer
    return {"user_id": user_id, "type": type(user_id).__name__}
```

_URL Example:_ `http://127.0.0.1:8000/users/10`

### Query Parameters

Query parameters are appended after a `?` in the URL, separated by `&`. They are usually optional and used for filtering, sorting, or pagination.

```python
@app.get("/search")
def search_items(q: str, limit: int = 10, skip: int = 0):
    return {"query": q, "limit": limit, "skip": skip}
```

_URL Example:_ `http://127.0.0.1:8000/search?q=python&limit=5&skip=0`

### Combining Path and Query Parameters

```python
@app.get("/users/{user_id}/posts")
def get_user_posts(user_id: int, category: str | None = None):
    return {"user_id": user_id, "category": category}
```

_URL Example:_ `http://127.0.0.1:8000/users/42/posts?category=tech`

---

## 6. Data Validation with Pydantic

**Pydantic** is used for data parsing and validation in Python. By inheriting from `pydantic.BaseModel`, you define the shape and types of the JSON payloads your API expects.

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0, description="The price must be greater than zero")
    in_stock: bool = True

app = FastAPI()

@app.post("/items")
def create_item(item: Item):
    # 'item' is automatically validated against the Item model
    return {"message": "Item created successfully", "data": item}
```

### What happens when validation fails?

If a client sends invalid data (e.g. `price: -10` or missing mandatory fields), FastAPI automatically returns a **`422 Unprocessable Entity`** response explaining exactly what failed, without requiring any manual `if/else` checks!

---

## 7. Complete In-Memory CRUD API Example

Here is a complete, working **Student Management API** that demonstrates full CRUD operations using an in-memory Python list.

Save this in `main.py`:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Student Management API")

# Pydantic Schemas
class StudentCreate(BaseModel):
    name: str = Field(min_length=2, example="Alice Smith")
    age: int = Field(gt=0, lt=120, example=20)
    course: str = Field(example="Computer Science")

class StudentResponse(BaseModel):
    id: int
    name: str
    age: int
    course: str

# In-memory database simulation
students_db: list[dict] = [
    {"id": 1, "name": "John Doe", "age": 21, "course": "Data Science"},
    {"id": 2, "name": "Jane Miller", "age": 22, "course": "Artificial Intelligence"}
]
id_counter = 2

# 1. READ ALL (GET)
@app.get("/students", response_model=list[StudentResponse])
def get_all_students():
    return students_db

# 2. READ ONE (GET)
@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return student
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with ID {student_id} not found"
    )

# 3. CREATE (POST)
@app.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate):
    global id_counter
    id_counter += 1
    new_student = {"id": id_counter, **student.model_dump()}
    students_db.append(new_student)
    return new_student

# 4. UPDATE (PUT)
@app.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, updated_student: StudentCreate):
    for index, student in enumerate(students_db):
        if student["id"] == student_id:
            updated_data = {"id": student_id, **updated_student.model_dump()}
            students_db[index] = updated_data
            return updated_data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with ID {student_id} not found"
    )

# 5. DELETE (DELETE)
@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int):
    for index, student in enumerate(students_db):
        if student["id"] == student_id:
            students_db.pop(index)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Student with ID {student_id} not found"
    )
```

---

## 8. HTTP Status Codes & Exception Handling

Standard HTTP status codes communicate the result of an API request to clients.

| Code      | Status Name               | Meaning                            | Common Use Case           |
| :-------- | :------------------------ | :--------------------------------- | :------------------------ |
| **`200`** | **OK**                    | Request succeeded                  | `GET`, `PUT` success      |
| **`201`** | **Created**               | Resource successfully created      | `POST` success            |
| **`204`** | **No Content**            | Succeeded, but no content returned | `DELETE` success          |
| **`400`** | **Bad Request**           | Invalid client input               | Business logic error      |
| **`401`** | **Unauthorized**          | Client lacks valid credentials     | Missing API key/JWT token |
| **`404`** | **Not Found**             | Resource does not exist            | Invalid ID provided       |
| **`422`** | **Unprocessable Entity**  | Request body validation failed     | Built-in Pydantic error   |
| **`500`** | **Internal Server Error** | Unexpected server crash            | Server-side bug           |

### Raising HTTP Exceptions

Use `HTTPException` from FastAPI to cleanly return error messages with appropriate HTTP status codes:

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    if item_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item ID out of allowed range."
        )
    return {"item_id": item_id}
```

---

## 9. Response Models

The `response_model` parameter in path operation decorators allows you to:

- Filter output data (hide sensitive fields like passwords or internal metadata).
- Validate response data structure.
- Auto-generate accurate OpenAPI documentation schemas.

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr

class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

app = FastAPI()

@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    # Even if we process 'password', the output will exclude it
    # because UserOut only defines 'username' and 'email'
    return user
```

---

## 10. Bonus Concepts: Folder Structure (Standard & `uv`) & Dependency Injection

### Standard Project Folder Structure (`pip` / Traditional)

```text
my_fastapi_app/
│
├── app/
│   ├── __init__.py
│   ├── main.py          # App initialization & router mounting
│   ├── dependencies.py  # Shared dependencies
│   │
│   ├── routers/         # API Route Handlers
│   │   ├── __init__.py
│   │   ├── students.py
│   │   └── courses.py
│   │
│   ├── schemas/         # Pydantic Models (Input/Output validation)
│   │   ├── __init__.py
│   │   └── student_schema.py
│   │
│   └── models/          # Database Models (ORMs like SQLAlchemy - future use)
│       └── __init__.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

### Project Folder Structure with `uv` (`src/` Package Layout)

When creating a production project using `uv init`, `uv` creates a `src/` layout with `pyproject.toml` and `uv.lock`.

```text
my-fastapi-app/
├── pyproject.toml         # Dependency & project configuration (managed by uv)
├── uv.lock                # Lockfile for exact reproducible builds
├── .python-version        # Pins Python version for uv
├── README.md              # Documentation
├── .gitignore
├── .venv/                 # Virtual environment (managed automatically by uv)
│
└── src/                   # Source root directory
    └── app/               # Main FastAPI application package
        ├── __init__.py
        ├── main.py        # App creation & router inclusions
        ├── config.py      # Environment & app settings
        ├── dependencies.py# Shared dependencies (DB sessions, Auth, etc.)
        │
        ├── routers/       # Modular route definitions
        │   ├── __init__.py
        │   ├── students.py
        │   └── courses.py
        │
        ├── schemas/       # Pydantic schemas for data validation
        │   ├── __init__.py
        │   └── student.py
        │
        └── models/        # Database models (ORMs like SQLAlchemy/SQLModel)
            └── __init__.py
```

#### Running a `src/` Layout App with `uv`

If `main.py` is located inside `src/app/main.py`:

```bash
uv run uvicorn app.main:app --reload
```

---

### Basics of Dependency Injection (`Depends`)

FastAPI features a powerful **Dependency Injection** system that makes it easy to reuse logic (like database sessions, authentication, or common query filters across endpoints).

```python
from fastapi import FastAPI, Depends

app = FastAPI()

# 1. Dependency function
def common_parameters(q: str | None = None, skip: int = 0, limit: int = 10):
    return {"q": q, "skip": skip, "limit": limit}

# 2. Inject dependency into endpoints
@app.get("/items")
def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users")
def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

---
