from fastapi import APIRouter
from services import AuthService
from db import schemas


router = APIRouter()

@router.post("/register/")
def register(user: schemas.User):
    """
    Đăng ký tài khoản
    """
    return AuthService.register(user.username, user.password)

# @router.post("/login/")
# def login(username: str, password: str):
#     """
#     Đăng nhập lấy token
#     """
#     # return AuthService.login(username, password)
#     return {"message" : "Chưa làm"}
