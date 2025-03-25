from dotenv import load_dotenv
import os
from fastapi import HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from db.models import User
from db import get_db

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

class AuthService:

    @staticmethod
    async def google_login(request: Request):
        return await oauth.google.authorize_redirect(request, REDIRECT_URI)

    @staticmethod
    def google_callback(request: Request, db: Session = Depends(get_db)):
        token = oauth.google.authorize_access_token(request)
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

    @staticmethod
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