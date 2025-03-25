from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth

from db import init_db
from api import router
from dotenv import load_dotenv
import os


from dotenv import load_dotenv
import os
from fastapi import HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from db.models import User
from db import get_db


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
app.add_middleware(SessionMiddleware, secret_key="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")

# Initialize OAuth
oauth = OAuth()


load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")


oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", 
)


# Initialize the database if it doesn't exist
init_db()

# Include API routes
app.include_router(router)


@app.get("/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, "http://localhost:8000/auth/google/callback")

@app.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid user info")

    email = user_info["email"]
    name = user_info.get("name", "Unknown User")
    avatar = user_info.get("picture", None)

    result = db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        user = User(email=email, name=name, avatar=avatar, provider="google")
        db.add(user)
        db.commit()
        db.refresh(user)

    return {"message": "Login successful", "user": {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar": user.avatar,
        "provider": user.provider
    }}

@app.get("/google/me")
def get_current_user(email: str, db: Session = Depends(get_db)):
    result = db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return {"user": {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "avatar": user.avatar,
        "provider": user.provider
    }}





# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
