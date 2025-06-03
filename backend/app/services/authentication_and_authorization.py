from fastapi import HTTPException, Depends, Response, Request
from jose import JWTError, jwt, ExpiredSignatureError
from authlib.integrations.starlette_client import OAuth
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from starlette.requests import Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from typing import Optional
import logging
import secrets
import os

from db.models import User
from db.schemas import UserBase

# Environment variables
load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
ACCESS_TOKEN_EXPIRE_MINUTES = 3000
COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days
FRONTEND_URL = os.getenv("FRONTEND_URL")
ENV = os.getenv("ENV")
with open("_ec_private_key.pem", "r") as f:
    PRIVATE_KEY = f.read()
with open("_ec_public_key.pem", "r") as f:
    PUBLIC_KEY = f.read()

# Initialize
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


# JWT for user management
def create_user_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if "sub" not in data:
        raise ValueError("Missing 'sub' field in data for token creation")
    payload = data.copy()
    payload["role"] = data.get("role", "free")
    payload["exp"] = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256")
    logging.info(f"Creating JWT for user: {data.get('sub')} with role: {payload['role']}")
    return token
def verify_user_access_token(
        request: Request,
        token: Optional[str] = None
) -> dict: # trả về email, role, exp
    """
    Xác thực JWT từ:
    - Header (Authorization: Bearer <token>)
    - Hoặc chuỗi token được truyền trực tiếp vào
    Trả về thông tin user: email, role, exp.
    """
    if not token:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, PUBLIC_KEY , algorithms="ES256")
        email: str = payload.get("sub")
        role: str = payload.get("role")
        exp: str = payload.get("exp")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"email": email, "role": role, "exp": exp}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# JWT for microservice management
def create_microservice_token(service_name: str, user_email: str) -> str:
    payload = {
        "iss": "text-to-everything-backend",
        "sub": service_name,
        "user_email": user_email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256")
    logging.info(f"Creating JWT for service: {service_name}")
    return token
def verify_microservice_token(
        request: Request,
        token: Optional[str] = None
) -> dict: # issuer, subject, user_email, iat, exp
    if not token:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms="ES256", issuer="text-to-everything-backend")
        return payload 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# Get user information
async def get_current_user(request: Request, db: Session) -> Optional[UserBase]:
    try:
        token = None
        if request.cookies.get("access_token"):
            token = request.cookies.get("access_token")
        else:
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
        
        if not token:
            return None

        payload = verify_token(token)
        email: str = payload.get("sub")
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            logging.warning(f"User not found in database: {email}")
            return None
        
        return UserBase(
            user.email,
            user.name,
            user.avatar,
            user.provider,
            user.role,
            user.expires_at
        )
        
    except HTTPException:
        # Try to refresh token if access token is expired
        refresh_token = request.cookies.get("refresh_token")
        if refresh_token:
            try:
                return await refresh_access_token(request, db)
            except:
                pass
        return None
async def get_user_info(request: Request, db: Session) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="No token provided")
    try:
        payload = verify_user_access_token(token)
        email = payload["email"]
        role = payload["role"]
        expire_at = payload["exp"]

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: email not found")
        
        user_info = {
            "email": email,
            "role": role,
            "expire": expire_at
        }
        logging.info(f"Give frontend this user-info: {user_info}")
        return user_info

    except Exception as e:
        print(f"An error occur when getting user information: {str(e)}")  
        raise HTTPException(status_code=401, detail="Invalid token")


# Login/Logout with Google and Github
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
async def provider_callback(request: Request, provider: str, db: Session):
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
        logging.info(f"---> Provider token: {token}")

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
        access_token = create_user_access_token(data={"sub": user.email, "role" : user.role})

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

