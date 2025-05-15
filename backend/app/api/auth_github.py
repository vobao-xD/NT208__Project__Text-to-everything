
from fastapi import APIRouter, Depends, Request, Response
from requests import Session
from api.auth import get_current_user
from db.models import User
from db import get_db
from services import auth_github as service


router=APIRouter()

@router.get("/github")
async def login(request: Request):
    return await service.GitHub.login_with_github(request)

@router.get("/github/callback")
async def login_callback(request: Request,db:Session=Depends(get_db)):
    return await service.GitHub.github_callback(request,db)
@router.get("/auth/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "avatar": current_user.avatar,
            "provider": current_user.provider,
            "role": current_user.role,
        }
    }