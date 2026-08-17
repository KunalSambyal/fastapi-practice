from fastapi import FastAPI
import uvicorn
from src.routers.cpu_router import router as cpu_router

app = FastAPI(title="PC Parts API")

app.include_router(cpu_router)


@app.get("/")
def root():
    return {"message": "Welcome to PC-Parts"}


if __name__ == "__main__":
    uvicorn.run(
        app="src.main:app", host="127.0.0.1", port=8000, log_level="info", reload=True
    )
