import contextlib
from sched import scheduler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from flask_limiter import RateLimitExceeded
from grpc import Status
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
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter

load_dotenv()

REDIS_URL=os.getenv("REDIS_URL")

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
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    print(f"FastAPI Limiter initialized with Redis at {REDIS_URL}")
    scheduler.add_job(check_expired_subscriptions, "interval", days=1)
    scheduler.start()
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=Status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": f"Bạn đã gửi quá nhiều tin nhắn. Hãy thử lại sau {round(exc.retry_after)} giây."}
    )
@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    logger.info("Ứng dụng FastAPI đã khởi động")
