# ⚡ FastAPI & Async SQLAlchemy 2.0 Mastery Guide

A comprehensive, production-ready guide and reference repository for building high-performance asynchronous REST APIs using **FastAPI**, **Pydantic v2**, and **Async SQLAlchemy 2.0**.

---

## 📑 Table of Contents

1. [Core Architectural Concepts](#1-core-architectural-concepts)
2. [Environment Setup & Package Management (`uv` & `pip`)](#2-environment-setup--package-management-uv--pip)
3. [FastAPI Fundamentals & HTTP Operations](#3-fastapi-fundamentals--http-operations)
4. [Pydantic v2 Schema Modeling & Validation](#4-pydantic-v2-schema-modeling--validation)
5. [Dependency Injection (`Depends`)](#5-dependency-injection-depends)
6. [Lifespan Management, Middleware & Security](#6-lifespan-management-middleware--security)
7. [Async Database Integration (SQLAlchemy 2.0 & PostgreSQL/SQLite)](#7-async-database-integration-sqlalchemy-20--postgresqlsqlite)
8. [Layered Architecture Pattern (DAO / Service / Controller)](#8-layered-architecture-pattern-dao--service--controller)
9. [Background Tasks & Global Exception Handling](#9-background-tasks--global-exception-handling)
10. [Project Structures & Running the Applications](#10-project-structures--running-the-applications)

---

## 1. Core Architectural Concepts

### What is an API & REST?

- **API (Application Programming Interface)**: A standardized interface enabling two distinct systems to exchange data over standard network protocols.
- **REST (Representational State Transfer)**: An architectural design pattern utilizing standard HTTP verbs (`GET`, `POST`, `PUT`, `DELETE`, `PATCH`) operating statelessly on resource-oriented URI paths (e.g., `/api/v1/cpus`, `/users/42`).

### Why FastAPI?

- **Asynchronous Performance**: Built on top of **Starlette** (ASGI) and **Pydantic v2** (Rust core), rivaling Node.js and Go benchmarks.
- **Automated Schema & Docs**: Generates dynamic **OpenAPI (Swagger UI at `/docs`)** and **ReDoc (at `/redoc`)** with zero extra code.
- **Type-Safe Validation**: Deeply integrated Python type hints guarantee static validation and runtime type coercion.

---

## 2. Environment Setup & Package Management (`uv` & `pip`)

### Option A: Ultra-Fast Setup with `uv` (Recommended ⚡)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package & project manager written in Rust.

```bash
# Initialize a new project
uv init my-fastapi-app
cd my-fastapi-app

# Add dependencies (creates .venv & uv.lock automatically)
uv add fastapi uvicorn "sqlalchemy[asyncio]" asyncpg pydantic

# Run development server
uv run uvicorn src.main:app --reload
```

### Option B: Traditional Setup with `venv` + `pip`

```bash
# Create and activate virtual environment
python -m venv .venv
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn src.main:app --reload
```

---

## 3. FastAPI Fundamentals & HTTP Operations

### Path Parameters vs. Query Parameters vs. Headers

```python
from fastapi import FastAPI, Path, Query, Header, Cookie
from typing import Optional

app = FastAPI(title="Parameter Demonstration")

@app.get("/items/{item_id}")
async def get_item(
    # Path parameter (identifies specific resource)
    item_id: int = Path(..., gt=0, description="The ID of the item"),
    # Query parameter (used for filtering/sorting/pagination)
    search: Optional[str] = Query(None, min_length=2, max_length=50),
    page: int = Query(1, ge=1),
    # Header & Cookie extraction
    user_agent: Optional[str] = Header(None),
    session_id: Optional[str] = Cookie(None)
):
    return {
        "item_id": item_id,
        "search": search,
        "page": page,
        "user_agent": user_agent
    }
```

### HTTP Verbs & Status Code Matrix

| Verb         | Action            | Idempotent | Success Code                | Common Status Codes                                    |
| :----------- | :---------------- | :--------- | :-------------------------- | :----------------------------------------------------- |
| **`GET`**    | Retrieve resource | Yes        | `200 OK`                    | `404 Not Found`                                        |
| **`POST`**   | Create / Action   | No         | `201 Created`               | `400 Bad Request`, `409 Conflict`, `422 Unprocessable` |
| **`PUT`**    | Full replacement  | Yes        | `200 OK` / `204 No Content` | `404 Not Found`, `400 Bad Request`                     |
| **`PATCH`**  | Partial update    | No         | `200 OK`                    | `404 Not Found`                                        |
| **`DELETE`** | Remove resource   | Yes        | `200 OK` / `204 No Content` | `404 Not Found`                                        |

---

## 4. Pydantic v2 Schema Modeling & Validation

Pydantic v2 uses a compiled Rust core (`pydantic-core`) providing fast data parsing, serialization, and schema validation.

```python
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr

class CpuBase(BaseModel):
    prd_code: str = Field(..., description="Unique hardware SKU code")
    brand: str | None = Field(default=None, description="Manufacturer brand (e.g., AMD, INTEL)")
    name: str = Field(..., min_length=2, max_length=100)
    core: int = Field(..., gt=0, description="Physical core count")
    thread: int = Field(..., gt=0, description="Logical thread count")
    base_clk: float = Field(default=1.0, ge=1.0, description="Base clock in GHz")
    boost_clk: float | None = Field(default=None, ge=1.0, description="Boost clock in GHz")
    price: float = Field(default=0.0, ge=0.0)
    updated_at: date = Field(default_factory=date.today)

    # Pydantic v2 Field Validator
    @field_validator("brand")
    @classmethod
    def normalize_brand(cls, v: str | None) -> str | None:
        if v:
            return v.strip().upper()
        return v

    # Pydantic v2 Config
    model_config = ConfigDict(
        from_attributes=True,         # Enables ORM model serialization (SQLAlchemy)
        str_strip_whitespace=True,    # Automatically trims strings
        json_schema_extra={
            "examples": [
                {
                    "prd_code": "AMD-7800X3D",
                    "brand": "AMD",
                    "name": "Ryzen 7 7800X3D",
                    "core": 8,
                    "thread": 16,
                    "base_clk": 4.2,
                    "boost_clk": 5.0,
                    "price": 449.00
                }
            ]
        }
    )

class CpuCreate(CpuBase):
    pass

class CpuResponse(CpuBase):
    id: int
```

---

## 5. Dependency Injection (`Depends`)

FastAPI's dependency injection system facilitates code reuse, authentication verification, and automatic resource lifecycle management.

### Database Session Generator & Reusable Pagination

```python
from collections.abc import AsyncGenerator
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import AsyncSessionFactory

# 1. Async Generator Dependency (Handles opening & closing connections cleanly)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        finally:
            await session.close()

# 2. Class-Based Query Dependency
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page index"),
        limit: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit

# 3. Usage in Route Handlers
@router.get("/cpus")
async def list_cpus(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # db is an active AsyncSession, pagination holds offset/limit
    pass
```

---

## 6. Lifespan Management, Middleware & Security

### Lifespan Context Manager (Modern Startup & Shutdown)

FastAPI replaced `@app.on_event("startup")` with `@asynccontextmanager` lifespans for predictable async resource management.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.database.connection import async_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # [STARTUP] Setup connection pools, warm caches
    print("🚀 Initializing database pool...")
    yield
    # [SHUTDOWN] Gracefully close pools and cleanup connections
    print("🛑 Disposing database pool...")
    await async_engine.dispose()

app = FastAPI(lifespan=lifespan)
```

### Security & CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import time

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom HTTP Middleware: Request Processing Duration Header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response
```

---

## 7. Async Database Integration (SQLAlchemy 2.0 & PostgreSQL/SQLite)

### Declarative Model Mapping (SQLAlchemy 2.0 `Mapped` Syntax)

```python
from datetime import date
from sqlalchemy import String, Integer, Float, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Cpu(Base):
    __tablename__ = "cpus"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prd_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    brand: Mapped[str | None] = mapped_column(String(30), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    core: Mapped[int] = mapped_column(Integer, nullable=False)
    thread: Mapped[int] = mapped_column(Integer, nullable=False)
    base_clk: Mapped[float] = mapped_column(Float, nullable=False)
    boost_clk: Mapped[float | None] = mapped_column(Float, nullable=True)
    socket: Mapped[str] = mapped_column(String(30), nullable=False)
    tdp: Mapped[int] = mapped_column(Integer, nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
```

### Async Database Session Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

DB_URL = "postgresql+asyncpg://postgres:password@localhost:5432/hardware_db"

async_engine = create_async_engine(DB_URL, echo=False, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False
)
```

---

## 8. Layered Architecture Pattern (DAO / Service / Controller)

In production services, decoupling routing from business logic and database queries maintains clean testability and code organization:

```
Request ──► Router (Path definition & response schema)
               └──► Controller (Request body / header parsing & status mapping)
                      └──► Service (Business logic & validations)
                             └──► DAO (Data Access Object / Raw database queries)
                                    └──► Database (PostgreSQL / SQLite)
```

### 1. Data Access Object (DAO Layer)

```python
from sqlalchemy import select
from src.database.helpers import fetch_all, fetch_one, create, update, delete_by_id
from src.models.cpu_model import Cpu

class CpuDAO:
    @staticmethod
    async def get_all() -> list[Cpu]:
        query = select(Cpu).order_by(Cpu.id)
        return await fetch_all(query)

    @staticmethod
    async def get_by_prd_code(prd_code: str) -> Cpu | None:
        query = select(Cpu).where(Cpu.prd_code == prd_code)
        return await fetch_one(query)
```

### 2. Business Service Layer

```python
class CpuService:
    @staticmethod
    async def save(**data) -> tuple[dict, int]:
        prd_code = data.get("prd_code")
        if not prd_code:
            return {"error": "Field 'prd_code' is required"}, 400

        existing = await CpuDAO.get_by_prd_code(str(prd_code))
        if existing:
            # Business update flow
            return {"id": existing.id, "status": "updated"}, 200
        else:
            # Business create flow
            new_id = await CpuDAO.create_cpu(CpuBase(**data))
            return {"id": new_id, "status": "created"}, 201
```

### 3. Controller Layer & Response Envelope

```python
from src.schemas.response_schema import APIResponse

async def cpu_controller(request: Request) -> ApiResponse:
    data = await get_request_data(request.headers.get("content-type", ""), request)
    match request.method:
        case "POST":
            result, status_code = await CpuService.save(**data)
            return APIResponse.success(data=result, code=status_code)
```

---

## 9. Background Tasks & Global Exception Handling

### Non-Blocking Background Tasks

```python
from fastapi import BackgroundTasks, APIRouter

router = APIRouter()

def send_audit_log(sku: str):
    # Simulated background task (e.g. logging, email notification)
    print(f"[Audit] New product created: {sku}")

@router.post("/items")
async def create_item(item: CpuCreate, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_audit_log, item.prd_code)
    return {"message": "Processing item creation..."}
```

### Global Custom Exception Handler

```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path
        }
    )
```

---

## 10. Project Structures & Running the Applications

### Repository Layout

```text
FastAPI/
├── main.py                   # Master educational reference (All concepts in one blueprint)
├── README.md                 # Complete documentation & study guide
├── .gitignore
│
├── src/                      # User Auth & Management API (Async SQLAlchemy + Router)
│   ├── main.py
│   ├── router.py
│   ├── db.py
│   ├── models.py
│   └── schemas.py
│
└── pc-parts-api/             # Production Layered PC Parts & CPU API
    ├── requirements.txt
    ├── .env.example
    └── src/
        ├── main.py           # Application Entrypoint
        ├── init_db.py        # Database migration & dummy data seeder
        ├── controllers/      # Request dispatching & handling
        ├── core/             # Helpers & utility functions
        ├── dao/              # Data Access Objects (DB query abstraction)
        ├── database/         # Engine, base declarative & session generators
        ├── models/           # SQLAlchemy 2.0 ORM Mapped models
        ├── routers/          # Modular API endpoint routes
        ├── schemas/          # Pydantic v2 DTO models
        └── services/         # Business domain logic
```

### How to Run the Applications

#### 1. Running the Master Reference Blueprint

```bash
uvicorn main:app --reload --port 8000
```

Interactive docs: `http://127.0.0.1:8000/docs`

#### 2. Running User Management API (`src/`)

```bash
# Run using module syntax from the root directory:
uvicorn src.main:app --reload --port 8000
```

#### 3. Running PC Parts API (`pc-parts-api/`)

```bash
cd pc-parts-api

# Step 1: Seed the database
python -m src.init_db

# Step 2: Start the server
uvicorn src.main:app --reload --port 8000
```

---

## 🎓 Summary of Mastered Skills

- [x] Asynchronous ASGI API lifecycle & lifespan context management
- [x] Pydantic v2 validation constraints, field validators, & custom `ConfigDict`
- [x] Async SQLAlchemy 2.0 declarative ORM (`Mapped`, `mapped_column`, `select`, `where`)
- [x] Modular routing with `APIRouter`
- [x] Dependency injection for database sessions & pagination (`Depends`)
- [x] Multi-tier layered architecture (DAO, Service, Controller, Router)
- [x] CORS, custom process timing middleware, and background tasks
- [x] Exception handling and standardized JSON response envelopes
- [x] Modern Python package & environment workflows (`uv` & `pip`)
