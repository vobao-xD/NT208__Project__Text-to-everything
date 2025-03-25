from fastapi import APIRouter, Depends
from services import AuthService as service
from db import schemas, get_db
from starlette.requests import Request
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

router = APIRouter()

@router.get("/google")
async def google_login(request: Request):
    return await service.google_login(request)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    return await service.google_callback(request, db)

@router.get("/google/login")
def get_current_user(email: str, db: Session = Depends(get_db)):
    return service.get_current_user(email, db)