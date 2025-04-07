
from fastapi import APIRouter, Depends, Request, Response
from requests import Session
from db import get_db
from services import auth_github as service


router=APIRouter()

@router.get("/github")
async def login(request: Request):
    return await service.GitHub.login_with_github(request)

@router.get("/github/callback")
async def login_callback(request: Request,db:Session=Depends(get_db)):
    return await service.GitHub.github_callback(request,db)
