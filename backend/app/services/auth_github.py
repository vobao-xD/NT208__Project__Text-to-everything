import os
import secrets
from fastapi.responses import RedirectResponse
from requests import request, session
from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from dotenv import load_dotenv
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

class GitHub:
    @staticmethod
    async def login_with_github(request: Request):
        #state = secrets.token_urlsafe(16)
        #request.session["oauth_state"] = state
        return await oauth.github.authorize_redirect(request)

    @staticmethod
    async def github_callback(request: Request, db: Session = Depends(get_db)):
        #stored_state = request.session.get("oauth_state")
        #received_state = request.query_params.get("state")

        #if stored_state != received_state:
        #    raise HTTPException(status_code=400, detail="CSRF detected: State mismatch")
    
        token = await oauth.github.authorize_access_token(request)
        user_resp = await oauth.github.get("user", token=token)
        
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info")
        #token_ddata=token.json()
        user_data = user_resp.json()
        email = user_data.get("email")

        # Nếu GitHub không trả về email, lấy từ API user/emails
        if email is None:
            emails_resp = await oauth.github.get("user/emails", token=token)
            if emails_resp.status_code == 200:
                email_data = emails_resp.json()
                email = next((e["email"] for e in email_data if e["primary"] and e["verified"]), None)
        
        if email is None:
            email = f"{user_data['id']}@github.com"

        name = user_data.get("name", "Unknown User")
        avatar = user_data.get("avatar_url", None)

        existing_user = db.execute(select(User).where(User.email == email)).scalars().first()

        if not existing_user:
            user = User(
                email=email,
                name=name,
                avatar=avatar,
                provider="github"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = existing_user
        #code=request.query_params("code")
        #github=GitHub(GITHUB_CLIENT_ID,GITHUB_CLIENT_SECRET)
        #auth = github.auth.as_web_user(code).exchange_token(github)
        #access_token = auth.token

        #session["access_token"] = access_token
        
        return {
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "avatar": user.avatar,
                "provider": user.provider,
            }
        }
