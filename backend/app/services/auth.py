import logging
import secrets
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Depends, Response, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from sqlalchemy.orm import Session
from db.models import User
from db import get_db
from fastapi.responses import RedirectResponse
import jwt
import bcrypt
from datetime import datetime
from core.security import create_access_token, SECRET_KEY, ALGORITHM
from sqlalchemy.future import select

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
    async def google_login(request: Request):
        state = secrets.token_urlsafe(32)
        request.session["state"] = state
        return await oauth.google.authorize_redirect(request, GOOGLE_REDIRECT_URI)

    @staticmethod
    async def google_callback(request: Request, db: Session = Depends(get_db)):
        provider_response = await oauth.google.authorize_access_token(request)
        user_info = provider_response.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="Invalid user info")

        email = user_info["email"]
        name = user_info.get("name", "Unknown User")
        avatar = user_info.get("picture", None)

        result = db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            user = User(email=email, name=name, avatar=avatar, provider="google", role="basic")
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token, "token_type": "bearer"}


    @staticmethod
    async def login_with_provider(request: Request, provider: str = "google"):
        state = secrets.token_urlsafe(32)
        request.session["state"] = state

        if provider == "google":
            redirect_uri = GOOGLE_REDIRECT_URI
        elif provider == "github":
            redirect_uri = GITHUB_REDIRECT_URI
        else:
            redirect_uri = f"http://localhost:8000/auth/{provider}/callback"

        try:
            redirect_uri = request.url_for('google_callback')
            logging.info(f"Redirect URI: {redirect_uri}")
            
            # Đảm bảo URL có protocol
            if not str(redirect_uri).startswith(('http://', 'https://')):
                redirect_uri = f"http://{redirect_uri}"
            # return await oauth.google.authorize_redirect(request, redirect_uri)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise

        logging.info(f"Redirecting to {provider} with redirect_uri: {redirect_uri}")
        try:
            return await getattr(oauth, provider).authorize_redirect(
                request, 
                redirect_uri=redirect_uri, 
                state=state
            )
        except Exception as e:
            logging.error(f"OAuth redirect failed for {provider}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"OAuth redirect failed: {str(e)}")

    # @staticmethod
    # async def provider_callback(request: Request, db: Session = Depends(get_db), provider: str = "google"):
    #     try:
            
    #         state = request.session.get("state")
    #         received_state = request.query_params.get("state")
            
    #         if not state or state != received_state:
    #             logging.error(f"State mismatch for {provider}: expected {state}, received {received_state}")
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"Invalid state parameter for {provider}: CSRF Warning!"
    #             )

    #         code = request.query_params.get("code")
    #         if not code:
    #             error = request.query_params.get("error")
    #             error_description = request.query_params.get("error_description", "")
    #             logging.error(f"OAuth error for {provider}: {error} - {error_description}")
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"OAuth authorization failed: {error} - {error_description}"
    #             )

    #         try:
    #             token = await getattr(oauth, provider).authorize_access_token(request)
    #         except Exception as e:
    #             logging.error(f"Failed to get access token for {provider}: {str(e)}")
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"Failed to exchange authorization code for access token: {str(e)}"
    #             )
            
    #         if provider == "google":
    #             user_resp = await oauth.google.get("userinfo", token=token)
    #         elif provider == "github":
    #             user_resp = await oauth.github.get("user", token=token)

    #         if user_resp.status_code != 200:
    #             logging.error(f"Failed to fetch user info for {provider}: {user_resp.status_code}")
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"Failed to fetch user info for {provider}: HTTP {user_resp.status_code}"
    #             )

    #         user_data = user_resp.json()
    #         logging.info(f"User data from {provider}: {user_data}")


    #         email = None
    #         if provider == "google":
    #             email = user_data.get("email")
    #             if not user_data.get("email_verified", False):
    #                 raise HTTPException(
    #                     status_code=400, 
    #                     detail="Email not verified by Google"
    #                 )
    #         elif provider == "github":
    #             email = user_data.get("email")
    #             # Nếu email private, lấy từ emails endpoint
    #             if not email:
    #                 try:
    #                     emails_resp = await oauth.github.get("user/emails", token=token)
    #                     if emails_resp.status_code == 200:
    #                         email_data = emails_resp.json()
    #                         # Lấy email primary và verified
    #                         primary_email = next(
    #                             (e for e in email_data if e.get("primary", False) and e.get("verified", False)), 
    #                             None
    #                         )
    #                         if primary_email:
    #                             email = primary_email["email"]
    #                 except Exception as e:
    #                     logging.warning(f"Failed to fetch GitHub emails: {str(e)}")

    #         if not email:
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"Email not provided by {provider} or email not verified"
    #             )

    #         provider_id = str(user_data.get("id", user_data.get("sub", "")))
    #         if not provider_id:
    #             raise HTTPException(
    #                 status_code=400, 
    #                 detail=f"User ID not provided by {provider}"
    #             )
            
    #         user_id = f"{provider}_{provider_id}"
    #         name = user_data.get("name", user_data.get("login", "Unknown User"))
    #         avatar = user_data.get("picture", user_data.get("avatar_url"))

    #         try:
    #             user = db.query(User).filter(User.email == email).first()
    #             if not user:
    #                 user = User(
    #                     id=user_id,
    #                     email=email,
    #                     name=name,
    #                     avatar=avatar,
    #                     provider=provider,
    #                 )
    #                 db.add(user)
    #                 logging.info(f"Created new user: {email} via {provider}")
    #             else:
    #                 if user.provider != provider:
    #                     raise HTTPException(status_code=400, detail="Email already registered with another provider")
    #                 user.name = name
    #                 user.avatar = avatar
    #                 user.id = user_id
    #                 logging.info(f"Updated existing user: {email} via {provider}")

    #             db.commit()
    #             db.refresh(user)
            
    #         except Exception as e:
    #             db.rollback()
    #             logging.error(f"Database error during {provider} login: {str(e)}")
    #             raise HTTPException(
    #                 status_code=500, 
    #                 detail=f"Database error during {provider} login"
    #             )
        
    #         try:
    #             access_token = create_access_token(data={"sub": user.id})
    #         except Exception as e:
    #             logging.error(f"Failed to create access token: {str(e)}")
    #             raise HTTPException(
    #                 status_code=500, 
    #                 detail="Failed to create access token"
    #             )
            
    #         response = RedirectResponse(url=f"{FRONTEND_URL}/generate")
    #         response.set_cookie(
    #             key="access_token",
    #             value=access_token,
    #             httponly=True,
    #             secure=ENV == "production",
    #             samesite="lax" if ENV == "development" else "strict",
    #             max_age=COOKIE_MAX_AGE,
    #             path="/",
    #             domain=None
    #         )

    #         if "state" in request.session:
    #             del request.session["state"]
            
    #         return response
    #     except Exception as e:
    #         logging.error(f"Unexpected error during {provider} login: {str(e)}")
    #         raise HTTPException(
    #             status_code=500, 
    #             detail=f"Unexpected error during {provider} login: {str(e)}"
    #         )

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

            if user_id is None:
                raise credentials_exception

            if exp and datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=401,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError as e:
            logging.error(f"JWT decode error: {str(e)}")
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def logout(request: Request, response: Response):
        response.delete_cookie("access_token", path="/")
        return RedirectResponse(url=f"{FRONTEND_URL}/login")