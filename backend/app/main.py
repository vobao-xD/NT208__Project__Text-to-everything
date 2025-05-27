from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from api import router
from db import init_db
import logging 
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the database if it doesn't exist
init_db()

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,  # Mức log tối thiểu (INFO trở lên)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Ghi log ra console
        logging.FileHandler("app.log")  # Ghi log ra file app.log
    ]
)

# Tạo logger riêng cho ứng dụng
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Sau này thay bằng frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)

# Configure session middleware with a secret key
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "super-secret-key"))

# Create img directory for storing images
if not os.path.exists("img"):
    os.mkdir("img")

# Mount img directory for serving static files
app.mount("/img", StaticFiles(directory="img"), name="static")

# Create static directory for serving static files
if not os.path.exists("static"):
    os.makedirs("static")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
    logger.info("Ứng dụng FastAPI đã khởi động")
