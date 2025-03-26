from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from db import init_db
from api import router
import os

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS for the app
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Session Middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=os.getenv("GOOGLE_CLIENT_SECRET"))

# Initialize the database if it doesn't exist
init_db()

# Include API routes
app.include_router(router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
