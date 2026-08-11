### 1. Path & Query Parameters

- Path parameters: `/students/{student_id}`
- Query parameters: `?age=18`
- Validation using `Path` and `Query`

### 2. Request Body Properly

- Pydantic models
- Nested models
- Optional and default fields
- Request models vs response models

### 3. Response Models

- `response_model`
- `response_model_exclude`
- Why passwords and other sensitive data should not be returned

### 4. Dependency Injection ⭐

- `Depends()`
- Creating reusable dependencies
- Understanding how dependencies work
- Why dependency injection is important for database integration

### 5. APIRouter Properly

- Router prefixes
- Router tags
- Separating routes into different routers
- Organizing larger FastAPI applications

### 6. Error Handling

- `HTTPException`
- Custom exceptions
- Appropriate HTTP status codes
- Handling validation and application errors

### 7. Middleware

- Understand what middleware does
- How requests and responses pass through middleware
- CORS middleware
- Creating basic custom middleware

### 8. Background Tasks

- `BackgroundTasks`
- Understanding when background tasks are useful
- Basic background task implementation

### 9. Testing

- `pytest`
- FastAPI `TestClient`
- Testing CRUD endpoints
- Testing validation errors
- Testing HTTP error responses
- Testing edge cases

---

## Next Phase

Once the above FastAPI basics are comfortable:

**_FastAPI Basics → PostgreSQL → SQLAlchemy → Database Integration → Authentication → Production Backend_**
