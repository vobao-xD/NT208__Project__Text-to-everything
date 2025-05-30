import contextlib
from sched import scheduler
from fastapi import FastAPI
from openai import AsyncOpenAI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from api import router
from services.check_expired_subscriptions import check_expired_subscriptions
from db import init_db
import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler
from openai_client_instance import lifespan
load_dotenv()
init_db()
scheduler = BackgroundScheduler()
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "super-secret-key"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)


if not os.path.exists("img"):
    os.mkdir("img")

app.mount("/img", StaticFiles(directory="img"), name="static")

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(router)
@app.on_event("startup")
async def startup_event():
    scheduler.add_job(check_expired_subscriptions, "interval", days=1)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    logger.info("Ứng dụng FastAPI đã khởi động")
