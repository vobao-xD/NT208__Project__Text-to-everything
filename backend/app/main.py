from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from db import init_db
from api import router
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the database if it doesn't exist
init_db()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for the app
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# # Configure Session Middleware for OAuth
# secret_key=os.getenv("SESSION_SECRET", None)
# if not secret_key:
#     raise ValueError("SESSION_SECRET environment variable is not set")

# app.add_middleware(SessionMiddleware, secret_key)

# Include API routes
app.include_router(router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
