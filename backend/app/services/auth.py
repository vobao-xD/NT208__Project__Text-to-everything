from fastapi import HTTPException, Depends, Response, APIRouter, Request
from core.security import create_access_token, SECRET_KEY, ALGORITHM
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from db.models import User
from datetime import datetime
from jose import jwt, JWTError
from db import get_db
import logging
import secrets
import os

load_dotenv()

# Environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")

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

class Auth:

    @staticmethod
    async def login_with_provider(request: Request, provider: str):
        # Kiểm tra provider
        if provider not in ["google", "github"]:
            raise HTTPException(status_code=400, detail="Provider không được hỗ trợ")
        if provider == "google":
            redirect_uri = GOOGLE_REDIRECT_URI
        elif provider == "github":
            redirect_uri = GITHUB_REDIRECT_URI
        logging.info(f"Redirecting to {provider} with redirect_uri: {redirect_uri}")
        
        # Chống CSRF
        state = secrets.token_urlsafe(32)
        request.session["state"] = state

        try:
            return await getattr(oauth, provider).authorize_redirect(request, redirect_uri, state=state)
        except Exception as e:
            logging.error(f"Redirect failed for {provider}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Không thể chuyển hướng đến {provider}")

    @staticmethod
    async def provider_callback(request: Request, provider: str, db: Session = Depends(get_db)):
        if provider not in ["google", "github"]:
            raise HTTPException(status_code=400, detail="Provider không được hỗ trợ")

        try:
            # Chống CSRF
            callback_state = request.session.get("state")
            received_state = request.query_params.get("state")
            if not callback_state or callback_state != received_state:
                logging.error(f"State mismatch for {provider}: expected {callback_state}, received {received_state}")
                raise HTTPException(status_code=400, detail=f"Invalid state parameter for {provider}: CSRF Warning!")

            # Lấy token từ provider
            token = await getattr(oauth, provider).authorize_access_token(request)

            if provider == "google":
                user_info = token.get("userinfo")
            elif provider == "github":
                user_response = await getattr(oauth, provider).get("user", token=token)
                user_info = user_response.json()
            if not user_info:
                raise HTTPException(status_code=400, detail=f"Failed to fetch user info for {provider}")

            # Trích xuất thông tin user
            email = user_info["email"]
            if not email:
                if provider == "google":
                    email = user_info.get("email")
                elif provider == "github":
                    emails_response = await getattr(oauth, provider).get("user/emails", token=token)
                    if emails_response.status_code == 200:
                        email_data = emails_response.json()
                        email = next((e["email"] for e in email_data if e["primary"] and e["verified"]), None)
            if not email:
                raise HTTPException(status_code=400, detail=f"Email not provided by {provider}")
            name = user_info.get("name", "Unknown User")
            avatar = user_info.get("picture", user_info.get("avatar_url"))

            # Lưu user vào database
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(email=email, name=name, avatar=avatar, provider=provider, role="basic")
                db.add(user)
            else:
                if user.provider != provider:
                    raise HTTPException(status_code=400, detail="Email already registered with another provider")
                user.name = name
                user.avatar = avatar
            db.commit()
            db.refresh(user)

            # Tạo access token
            access_token = create_access_token(data={"sub": user.email})

            # Redirect về frontend (không cần truyền email qua query parameter)
            redirect_url = f"{FRONTEND_URL}/generate"
            response = RedirectResponse(url=redirect_url)

            # Thiết lập cookie với access_token
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
            email: str = payload.get("sub")
            exp = payload.get("exp")

            if email is None:
                raise credentials_exception

            if exp and datetime.utcnow().timestamp() > exp:
                logging.warning(f"Token expired for email: {email}")
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = db.query(User).filter(User.email == email).first()
            if not user:
                logging.error(f"User not found for email: {email}")
                raise credentials_exception
            return user
        
        except JWTError as e:
            logging.error(f"JWT decode error: {str(e)}")
            raise credentials_exception

    @staticmethod
    async def logout(request: Request, response: Response):
        if request.cookies.get("access_token"):
            response.delete_cookie(
                key="access_token",
                path="/",
                httponly=True,
                secure=os.getenv("ENV") == "production",
                samesite="lax"
            )
        # Xóa session nếu có
        request.session.clear()
        logging.info("User logged out successfully")
        return RedirectResponse(url=f"{FRONTEND_URL}/login")