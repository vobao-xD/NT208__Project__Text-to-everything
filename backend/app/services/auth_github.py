import logging
import os
import secrets
import uuid
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
import jwt
from requests import request, session
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from dotenv import load_dotenv
from core.security import create_access_token
from db.models import User
from db.database import get_db
from sqlalchemy.orm import Session

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

oauth = OAuth()
oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    redirect_uri=GITHUB_REDIRECT_URI,
    client_kwargs={"scope": "user:email"},  
)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class GitHub:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def login_with_github(request: Request):
        state = secrets.token_urlsafe(16)
        request.session["state"] = state
        return await oauth.github.authorize_redirect(request, state=state)

    @staticmethod
    async def github_callback(request: Request, db: Session = Depends(get_db)):
        try:
            state = request.session.get("state")
            if not state or state != request.query_params.get("state"):
                raise HTTPException(status_code=400, detail="Invalid state parameter")

            token = await oauth.github.authorize_access_token(request)
            user_resp = await oauth.github.get("user", token=token)
            if user_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to fetch user info")

            user_data = user_resp.json()
            email = user_data.get("email")

            if email is None:
                emails_resp = await oauth.github.get("user/emails", token=token)
                if emails_resp.status_code == 200:
                    email_data = emails_resp.json()
                    email = next((e["email"] for e in email_data if e["primary"] and e["verified"]), None)

            if email is None:
                raise HTTPException(status_code=400, detail="Email not provided by GitHub")

            github_id = str(user_data['id'])
            user_id = f"github_{github_id}"  # Hoặc dùng UUID nếu bạn chọn Cách 2
            name = user_data.get("name", "Unknown User")
            avatar = user_data.get("avatar_url")

            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    id=user_id,
                    email=email,
                    name=name,
                    avatar=avatar,
                    provider="github",
                )
                db.add(user)
            else:
                if user.provider == "github":
                    user.name = name
                    user.avatar = avatar
                else:
                    user_id = f"github_{github_id}"
                    user = User(
                        id=user_id,
                        email=email,
                        name=name,
                        avatar=avatar,
                        provider="github",
                    )
                    db.add(user)

            db.commit()
            db.refresh(user)

            access_token = create_access_token(data={"sub": user.id})
            
            # Redirect đến frontend với access_token
            frontend_redirect_url = f"http://localhost::5173/auth/callback?token={access_token}"
            return RedirectResponse(url=frontend_redirect_url)
        except Exception as e:
            logging.error(f"GitHub login failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"GitHub login failed: {str(e)}")