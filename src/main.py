from fastapi import FastAPI
from .router import router

app = FastAPI(title="User Management")


@app.get("/")
async def root():
    return {"message": "Welcome", "health": "ok"}


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
