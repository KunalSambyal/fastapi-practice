"""
==================================================================================
FASTAPI & PYDANTIC V2 MASTER PRODUCTION REFERENCE & BLUEPRINT
==================================================================================
A comprehensive, production-ready reference covering modern FastAPI architecture,
Pydantic v2 models, dependency injection, OAuth2 JWT auth, middleware, async/await,
background tasks, CORS, and OpenAPI documentation standards.

MODULE BREAKDOWN:
1. Lifespan Context Manager & App Initialization
2. CORS & Custom Timing Middleware
3. Pydantic v2 Schema Modeling, Field Validation, & ConfigDict
4. Path, Query, Header, Cookie, & Body Parameters
5. Dependency Injection System (get_db, Auth verification)
6. Asynchronous Endpoints & Background Tasks
7. Custom Error Handling & Global Exception Handlers
8. Modular APIRouter Setup
"""

import time
import logging
from typing import List, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI, APIRouter, Depends, HTTPException, status, 
    Path, Query, Header, Cookie, Body, BackgroundTasks, Request
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fastapi_reference")

# ==============================================================================
# MODULE 1: LIFESPAN CONTEXT MANAGER (STARTUP & SHUTDOWN)
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager replaces legacy startup/shutdown events.
    Executes database pool connection on startup and cleanup on shutdown.
    """
    logger.info("[Startup] Initializing Database Connection Pool & Cache...")
    yield
    logger.info("[Shutdown] Closing Database Connection Pool & Freeing Resources...")

# Main FastAPI Application Instance
app = FastAPI(
    title="Production FastAPI & Pydantic v2 Master Reference",
    description="Comprehensive architectural reference for high-performance Async APIs.",
    version="2.0.0",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc Interface
    lifespan=lifespan
)

# ==============================================================================
# MODULE 2: CORS & CUSTOM MIDDLEWARE
# ==============================================================================
# Cross-Origin Resource Sharing (CORS) Security Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://myfrontend.com"], # Strict origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Custom HTTP Middleware for Request Process Timing & X-Process-Time Header
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# ==============================================================================
# MODULE 3: PYDANTIC V2 SCHEMA MODELING & VALIDATION
# ==============================================================================
class ItemBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="Title of the item")
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Price must be strictly positive")
    tags: List[str] = Field(default_factory=list)

    # Pydantic v2 Custom Field Validator
    @field_validator("title")
    @classmethod
    def validate_title_case(cls, v: str) -> str:
        if v[0].islower():
            return v.capitalize()
        return v

    model_config = ConfigDict(
        str_strip_whitespace=True, # Automatically strips leading/trailing whitespace
        json_schema_extra={
            "example": {
                "title": "Ergonomic Gaming Mouse",
                "description": "High-precision 26,000 DPI optical sensor mouse",
                "price": 79.99,
                "tags": ["electronics", "gaming", "peripherals"]
            }
        }
    )

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    created_at: str

    model_config = ConfigDict(from_attributes=True) # Enables ORM compatibility (SQLAlchemy/SQLModel)

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==============================================================================
# MODULE 4: DEPENDENCY INJECTION SYSTEM (Depends)
# ==============================================================================
# OAuth2 Password Bearer Scheme for Swagger UI Token Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_db_session() -> AsyncGenerator[str, None]:
    """
    Simulated Database Session Dependency Generator.
    Yields DB session to endpoint and guarantees cleanup after response.
    """
    db_session = "AsyncSQLAlchemySession_#104"
    try:
        logger.info(f"Connected to DB Session: {db_session}")
        yield db_session
    finally:
        logger.info(f"Closed DB Session: {db_session}")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    Simulated JWT Token Verification Dependency.
    """
    if token != "secret_super_token_123":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse(id=1, username="alex_developer", email="alex@example.com")

class CommonPagination:
    """Class-based dependency for standard query parameters."""
    def __init__(self, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit

# ==============================================================================
# MODULE 5: MODULAR API ROUTER (API v1)
# ==============================================================================
api_router = APIRouter(prefix="/api/v1", tags=["V1 Endpoints"])

# Authentication Endpoint
@api_router.post("/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "admin" and form_data.password == "password123":
        return Token(access_token="secret_super_token_123", token_type="bearer")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )

# Protected Endpoint Requiring Authentication & Dependency Injection
@api_router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

# CRUD Endpoint with Path, Query, & Body Validation
@api_router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    background_tasks: BackgroundTasks,
    db: str = Depends(get_db_session),
    user_agent: Optional[str] = Header(None)
):
    """
    Creates a new item, writes to DB session, and dispatches background task.
    """
    logger.info(f"User-Agent: {user_agent}")
    
    # Non-blocking Background Task (e.g. send email notification / audit log)
    background_tasks.add_task(send_audit_notification, item.title)

    return ItemResponse(
        id=101,
        title=item.title,
        description=item.description,
        price=item.price,
        tags=item.tags,
        created_at="2026-08-13T22:18:00Z"
    )

@api_router.get("/items", response_model=List[ItemResponse])
async def list_items(
    pagination: CommonPagination = Depends(),
    db: str = Depends(get_db_session)
):
    """
    Retrieves paginated list of items using class-based dependency injection.
    """
    return [
        ItemResponse(
            id=i,
            title=f"Sample Product #{i}",
            description="High quality learning material",
            price=19.99 * i,
            tags=["sample", "fastapi"],
            created_at="2026-08-13T22:18:00Z"
        ) for i in range(1, pagination.limit + 1)
    ]

# Background Task Function
def send_audit_notification(item_title: str):
    logger.info(f"[Background Task] Audit notification dispatched for created item: '{item_title}'")

# Include Router in main App
app.include_router(api_router)

# ==============================================================================
# MODULE 6: CUSTOM GLOBAL EXCEPTION HANDLER
# ==============================================================================
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path
        }
    )

# Root Health Check Endpoint
@app.get("/", tags=["Health Check"])
async def root_health_check():
    return {
        "status": "healthy",
        "service": "FastAPI Master Reference API",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    # Runs ASGI server locally on http://127.0.0.1:8000
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
