from fastapi import APIRouter, Depends
from services import AuthService as service, oauth2_scheme
from db import get_db
from starlette.requests import Request
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/google")
async def google_login(request: Request):
    return await service.google_login(request)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    return await service.google_callback(request, db)

@router.get("/user/me")
def get_current_user(token: str, db: Session = Depends(get_db)):
    return service.get_current_user(token, db)
