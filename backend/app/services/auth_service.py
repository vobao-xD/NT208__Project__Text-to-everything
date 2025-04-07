from dotenv import load_dotenv
import os
from fastapi import HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from db.models import User
from db import get_db
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from core import *

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Initialize OAuth
oauth = OAuth()

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

# OAuth2 Bearer Token (JWT)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class AuthService:

    @staticmethod
    async def google_login(request: Request):
        return await oauth.google.authorize_redirect(request, REDIRECT_URI)

    @staticmethod
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

        access_token = create_access_token(data={"sub": user.email})
        redirect_url = f"http://127.0.0.1:5500/frontend/generate.html"
        return RedirectResponse(url=redirect_url)
        #return {"access_token": access_token, "token_type": "bearer"} 

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        email = decode_access_token(token) 
        user = db.query(User).filter(User.email == email).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")

        return {
            "message" : "Login successfully!",
            "id": user.id, 
            "email": user.email, 
            "name": user.name, 
            "avatar": user.avatar
        }