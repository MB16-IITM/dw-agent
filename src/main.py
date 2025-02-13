from fastapi import FastAPI
from src.routes.run import router as run_router
from src.routes.read import router as read_router

app = FastAPI()
app.include_router(run_router)
app.include_router(read_router)
