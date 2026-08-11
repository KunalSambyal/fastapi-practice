from fastapi import FastAPI
from learn.path_and_querry_01 import router

app = FastAPI()

app.include_router(router)
