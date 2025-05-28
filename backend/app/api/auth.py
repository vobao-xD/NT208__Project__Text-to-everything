from fastapi import APIRouter, Depends, Response
from services.auth import Auth
from db import get_db
from starlette.requests import Request
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/auth/github") 
async def github_login(request: Request):
    return await Auth.login_with_provider(request, "github")

@router.get("/auth/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    return await Auth.provider_callback(request, db, "github")

@router.get("/auth/google") 
async def google_login(request: Request):
    return await Auth.google_login(request)
    return await Auth.login_with_provider(request, "google")

@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    return await Auth.google_callback(request, db)
    return await Auth.provider_callback(request, db, "google")

@router.get("/auth/logout")
async def logout(request: Request, response: Response):
    return await Auth.logout(request, response)