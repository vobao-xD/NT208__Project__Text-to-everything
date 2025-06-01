from fastapi import APIRouter, Depends, Response
from services.auth import Auth
from db import get_db
from starlette.requests import Request
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/auth/github") 
async def github_login(request: Request):
    """
        Chuyển hướng người dùng đến trang đăng nhập GitHub để xác thực.

        **Input**:
        - None (Không yêu cầu tham số trong request).

        **Output**:
        - **Redirect**: Chuyển hướng đến trang đăng nhập GitHub.

        **Responses**:
        - **200**: Chuyển hướng thành công.
        - **500**: Lỗi server nếu cấu hình OAuth thất bại.
        ```json
        {
            "detail": "Không thể chuyển hướng đến github"
        }
        ```

        **Lưu ý**:
        - Frontend cần xử lý redirect từ GitHub callback.
    """
    return await Auth.login_with_provider(request, "github")

@router.get("/auth/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """
        Xử lý callback từ GitHub, lấy thông tin user, lưu vào database, tạo access token và lưu vào cookie.

        **Input**: được truyền từ backend

        **Output**:
        - **Redirect**: Chuyển hướng đến `{FRONTEND_URL}/generate` (mặc định: `http://localhost:5173/generate`).
        - **Cookie**:
            - `access_token` (str): JWT token, `httponly`, `secure` (trong production), `samesite=lax`, hết hạn sau 30 ngày.

        **Responses**:
        - **200**: Chuyển hướng thành công với cookie `access_token`.
        - **400**: Lỗi nếu `state` không hợp lệ, email không lấy được, hoặc email đã đăng ký với provider khác.
        ```json
        {
            "detail": "Invalid state parameter for github: CSRF Warning!"
        }
        ```
        - **500**: Lỗi server nếu không lấy được token hoặc thông tin user.
        ```json
        {
            "detail": "github login failed: <error_message>"
        }
        ```

        **Lưu ý**:
        - Nếu GitHub không cung cấp email công khai, API sẽ gọi `/user/emails` để lấy email verified.
    """
    return await Auth.provider_callback(request, "github", db)

@router.get("/auth/google") 
async def google_login(request: Request):
    """
        Chuyển hướng người dùng đến trang đăng nhập Google để xác thực.

        **Input**: không có, chỉ cần gọi auth/login

        **Output**:
        - **Redirect**: Chuyển hướng đến trang đăng nhập Google, không trực tiếp trả kết quả

        **Responses**: trả về cho frontend những thứ sau
        - **200**: Chuyển hướng thành công.
        - **500**: Lỗi server nếu cấu hình OAuth thất bại. Định dạng trả về:
        ```json
        {
            "detail": "Không thể chuyển hướng đến google"
        }
        ```
        **Lưu ý**:
        - Frontend cần xử lý redirect từ Google callback.
    """
    return await Auth.login_with_provider(request, "google")

@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
        Xử lý callback từ Google sau khi xác thực, lưu user vào database, tạo access token và lưu vào cookie.

        **Input**:
        - **Query Parameters**: được gọi bởi backend, backend tự bỏ vô

        **Output**:
        - **Redirect**: Chuyển hướng đến `{FRONTEND_URL}/generate` (mặc định: `http://localhost:5173/generate`).
        - **Cookie**:
            - `access_token` (str): JWT token, `httponly`, `secure` (trong production), `samesite=lax`, hết hạn sau 30 ngày.

        **Responses**:
        - **200**: Chuyển hướng thành công với cookie `access_token`.
        - **400**: Lỗi nếu `state` không hợp lệ, email không lấy được, hoặc email đã đăng ký với provider khác.. Định dạng lỗi:
        ```json
        {
            "detail": "Invalid state parameter for google: CSRF Warning!"
        }
        ```
        - **500**: Lỗi server nếu không lấy được token hoặc thông tin user. Định dạng lỗi:
        ```json
        {
            "detail": "google login failed: <error_message>"
        }
        ```
    """
    return await Auth.provider_callback(request, "google", db)

@router.get("/auth/logout")
async def logout(request: Request, response: Response):
    """
        Đăng xuất người dùng, xóa cookie `access_token` và session, chuyển hướng về trang đăng nhập.

        **Input**:
        - None (Không yêu cầu tham số trong request).

        **Output**:
        - **Redirect**: Chuyển hướng đến `{FRONTEND_URL}/login` (mặc định: `http://localhost:5173/login`).

        **Responses**:
        - **200**: Đăng xuất thành công, cookie và session được xóa, không có mã lỗi khác
        - **Notes**: Cookie chỉ bị xóa nếu tồn tại.

        **Lưu ý**:
        - Frontend cần xử lý redirect để hiển thị trang đăng nhập.
    """
    return await Auth.logout(request, response)