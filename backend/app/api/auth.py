from fastapi import APIRouter
from services.auth_service import AuthService

router = APIRouter()

@router.post("/register/")
def register(username: str, password: str):
    """
    Đăng ký tài khoản
    """
    # return AuthService.register(username, password)
    pass

@router.post("/login/")
def login(username: str, password: str):
    """
    Đăng nhập lấy token
    """
    # return AuthService.login(username, password)
    pass
