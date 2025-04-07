from fastapi import APIRouter
from db import get_db
router = APIRouter()

# API trả về trang chủ của web
@router.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything API"}

# API để ngăn truy cập vào docs
# @router.get("/docs")
# def do_nothing():
#     return {"message": "What r u doing bro???"}

# API để ngăn truy cập vào redoc
# @router.get("/redoc")
# def do_nothing():
#     return {"message": "What r u doing bro???"}