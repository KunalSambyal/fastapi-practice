from fastapi import FastAPI
from app.routes.user_router import router as user_router

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(user_router)
