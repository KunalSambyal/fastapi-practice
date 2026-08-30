from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import async_engine
from app.models.user_model import Base
from app.routes.user_router import router as user_router
from app.routes.notes_router import notes_router
from app.models.notes_model import Note


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


app.include_router(user_router)
app.include_router(notes_router)
