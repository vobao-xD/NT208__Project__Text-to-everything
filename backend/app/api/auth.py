from fastapi import APIRouter
from services import AuthService as service
from db import schemas
from starlette.requests import Request

router = APIRouter()