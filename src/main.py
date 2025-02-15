from fastapi import FastAPI
from src.routes.run import router as run_router
from src.routes.read import router as read_router
import logging


app = FastAPI()
app.include_router(run_router)
app.include_router(read_router)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/data/app.log'),
        logging.StreamHandler()
    ]
)