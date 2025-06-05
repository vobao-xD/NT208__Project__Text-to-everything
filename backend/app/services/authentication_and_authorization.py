from fastapi import HTTPException, Response, Request
from jose import JWTError, jwt, ExpiredSignatureError
from authlib.integrations.starlette_client import OAuth
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
FRONTEND_URL = os.getenv("BASE_FRONTEND_URL")
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

# Ultilities
def decode_user_jwt(token: str) -> dict:
    """
    Hàm nội bộ để giải mã JWT và trả về payload.
    Trả về: dict chứa email, role, exp.
    """
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        exp: int = payload.get("exp")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid token: email not found")
        if not exp:
            raise HTTPException(status_code=401, detail="Invalid token: expiration not found")
        
        return {
            "email": email,
            "role": role or "free",  # Gán role mặc định nếu không có
            "exp": exp
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
def decode_microservice_jwt(token: str, expected_issuer: str = "text-to-everything-backend") -> dict:
    """
    Hàm nội bộ để giải mã JWT và trả về payload.
    Trả về: dict chứa issuer, subject, user_email, iat, exp.
    """
    try:
        payload = jwt.decode(token, PUBLIC_KEY, algorithms=["ES256"], options={"verify_iss": True}, issuer=expected_issuer)
        issuer: str = payload.get("iss")
        subject: str = payload.get("sub")
        user_email: str = payload.get("user_email")
        iat: int = payload.get("iat")
        exp: int = payload.get("exp")

        if not issuer or issuer != expected_issuer:
            raise HTTPException(status_code=401, detail="Invalid token: issuer mismatch")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token: user_email not found")
        if not exp:
            raise HTTPException(status_code=401, detail="Invalid token: expiration not found")

        return {
            "issuer": issuer,
            "subject": subject or "who the fuck make this token???",
            "user_email": user_email,
            "iat": iat or 0,  # Gán mặc định nếu iat không có
            "exp": exp
        }
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# JWT for user management
def create_user_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    if "sub" not in data:
        raise ValueError("Missing 'sub' field in data for token creation")
    payload = data.copy()
    payload["role"] = data.get("role", "free")
    payload["exp"] = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="ES256")
    # logging.info(f"Creating JWT for user: {data.get('sub')} with role: {payload['role']}")
    return token
def verify_user_access_token(
    *,  # Buộc sử dụng keyword arguments
    source: str = "direct",
    token: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Xác thực JWT từ nguồn được chỉ định:
    - source="direct": Token truyền trực tiếp
    - source="header": Token từ header Authorization: Bearer <token>
    - source="cookie": Token từ cookie access_token
    Trả về: dict chứa email, role, exp.
    """
    if source not in ["direct", "header", "cookie"]:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'direct', 'header', or 'cookie'")

    if source == "direct":
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        logging.info(f"Verifying token (direct): {token}")
        return decode_user_jwt(token)

    if source == "header":
        if not request:
            raise HTTPException(status_code=401, detail="Request object required for header source")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        logging.info(f"Verifying token (header): {token}")
        return decode_user_jwt(token)

    if source == "cookie":
        if not request:
            raise HTTPException(status_code=401, detail="Request object required for cookie source")
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="No token found in cookies")
        logging.info(f"Verifying token (cookie): {token}")
        return decode_user_jwt(token)
    
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
    # logging.info(f"Creating JWT for service: {service_name}")
    return token
def verify_microservice_token(
    *,  # Buộc sử dụng keyword arguments
    source: str = "direct",
    token: Optional[str] = None,
    request: Optional[Request] = None
) -> dict:
    """
    Xác thực JWT từ nguồn được chỉ định:
    - source="direct": Token truyền trực tiếp
    - source="header": Token từ header Authorization: Bearer <token>
    Trả về: dict chứa issuer, subject, user_email, iat, exp.
    """
    if source not in ["direct", "header"]:
        raise HTTPException(status_code=400, detail="Invalid source. Must be 'direct' or 'header'")

    if source == "direct":
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        logging.info(f"Verifying microservice token (direct): {token}")
        return decode_microservice_jwt(token)

    if source == "header":
        if not request:
            raise HTTPException(status_code=401, detail="Request object required for header source")
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
        token = auth_header.split(" ")[1]
        logging.info(f"Verifying microservice token (header): {token}")
        return decode_microservice_jwt(token)

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

        payload = verify_user_access_token(token)
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
        return None
async def get_user_info(request: Request, db: Session) -> dict: # Hỗ trợ cả header lẫn cookie
    """
    Lấy thông tin user từ token, ưu tiên cookie, sau đó header.
    Trả về: dict chứa email, role, expire.
    """
    try:
        # Ưu tiên cookie, sau đó header
        try:
            payload = verify_user_access_token(source="cookie", request=request)
        except HTTPException as e:
            if e.status_code == 401 and "No token found in cookies" in e.detail:
                payload = verify_user_access_token(source="header", request=request)
            else:
                raise e
        
        user_info = {
            "email": payload["email"],
            "role": payload["role"],
            "expire": payload["exp"]
        }
        logging.info(f"User info for frontend: {user_info}")
        return user_info

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error getting user info: {str(e)}")
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
async def log_out(request: Request, response: Response):
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

