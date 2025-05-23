import logging
import secrets
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Response, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from db.models import User
from db import get_db
from fastapi.responses import RedirectResponse
import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000
COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ENV = os.getenv("ENV", "development")

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or user.provider != "form" or not bcrypt.checkpw(form_data.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.id})
    response = Response()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=ENV == "production",
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/"
    )
    return {"message": "Login successful"}
async def register(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == form_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = bcrypt.hashpw(form_data.password.encode(), bcrypt.gensalt()).decode()
    user_id = f"form_{secrets.token_hex(16)}"
    user = User(
        id=user_id,
        email=form_data.username,
        name=form_data.username,
        password=hashed_password,
        provider="form",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    response = Response()
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=ENV == "production",
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/"
    )
    return {"message": "Registration successful"}

class Auth:
    @staticmethod
    async def login_with_provider(request: Request, provider: str):
        state = secrets.token_urlsafe(16)
        request.session["state"] = state
        redirect_uri = os.getenv(f"{provider.upper()}_REDIRECT_URI", f"http://localhost:8000/auth/{provider}/callback")
        logging.info(f"Redirecting to {provider} with redirect_uri: {redirect_uri}")
        return await getattr(oauth, provider).authorize_redirect(request, redirect_uri=redirect_uri, state=state)

    @staticmethod
    async def provider_callback(request: Request, db: Session = Depends(get_db), provider: str = "github"):
        try:
            state = request.session.get("state")
            received_state = request.query_params.get("state")
            if not state or state != received_state:
                logging.error(f"State mismatch for {provider}: expected {state}, received {received_state}")
                raise HTTPException(status_code=400, detail=f"Invalid state parameter for {provider}: CSRF Warning!")

            token = await getattr(oauth, provider).authorize_access_token(request)
            user_resp = await getattr(oauth, provider).get("userinfo" if provider == "google" else "user", token=token)
            if user_resp.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch user info for {provider}")

            user_data = user_resp.json()
            email = user_data.get("email")
            if not email:
                if provider == "google":
                    email = user_data.get("email")
                elif provider == "github":
                    emails_resp = await getattr(oauth, provider).get("user/emails", token=token)
                    if emails_resp.status_code == 200:
                        email_data = emails_resp.json()
                        email = next((e["email"] for e in email_data if e["primary"] and e["verified"]), None)

            if not email:
                raise HTTPException(status_code=400, detail=f"Email not provided by {provider}")

            provider_id = str(user_data.get("id", user_data.get("sub")))
            user_id = f"{provider}_{provider_id}"
            name = user_data.get("name", "Unknown User")
            avatar = user_data.get("picture", user_data.get("avatar_url"))

            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    id=user_id,
                    email=email,
                    name=name,
                    avatar=avatar,
                    provider=provider,
                )
                db.add(user)
            else:
                if user.provider != provider:
                    raise HTTPException(status_code=400, detail="Email already registered with another provider")
                user.name = name
                user.avatar = avatar

            db.commit()
            db.refresh(user)

            access_token = create_access_token(data={"sub": user.id})
            response = RedirectResponse(url=f"{FRONTEND_URL}/generate")
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=ENV == "production",
                samesite="lax",
                max_age=COOKIE_MAX_AGE,
                path="/"
            )
            return response
        except Exception as e:
            logging.error(f"{provider} login failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"{provider} login failed: {str(e)}")

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            exp = payload.get("exp")
            if user_id is None or (exp and datetime.utcnow().timestamp() > exp):
                raise credentials_exception
        except jwt.PyJWTError:
            raise credentials_exception
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def logout(request: Request, response: Response):
        response.delete_cookie("access_token", path="/")
        return RedirectResponse(url=f"{FRONTEND_URL}/login")