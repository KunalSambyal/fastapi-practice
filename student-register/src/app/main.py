from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.student_router import router as student_router

app = FastAPI(title="Student Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
