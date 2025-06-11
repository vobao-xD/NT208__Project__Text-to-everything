import mimetypes
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from services.authentication_and_authorization import verify_user_access_token
router = APIRouter()

# API trả về trang chủ của web
@router.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything"}

@router.get("/get-output/{filename:path}")
async def serve_output_file(
    filename: str,
    request: Request
):
    """
    Lấy các file sản phẩm của AI (audio, image, video, text, v.v.) từ thư mục _outputs/.
    Args:
        filename: Đường dẫn file trong thư mục _outputs/ (ví dụ: _outputs/user@example.com/audio/abc.mp3).
        request: Request chứa header để xác thực.
    Returns:
        FileResponse: File với media_type tương ứng (audio/mpeg, image/png, video/mp4, text/plain, v.v.).
    Raises:
        HTTPException: Nếu file không tồn tại, không có quyền truy cập, hoặc lỗi server.
    """
    try:
        # Xác thực người dùng
        # user_data = verify_user_access_token(source="cookie", request=request)

        # Chuẩn hóa đường dẫn file
        file_path = Path(filename)
        outputs_dir = Path("_outputs")

        # Kiểm tra file có nằm trong _outputs/ không
        if not str(file_path).startswith(str(outputs_dir) + "/"):
            raise HTTPException(status_code=403, detail="Access to files outside _outputs directory is forbidden")

        # Kiểm tra quyền sở hữu (giả sử file_path chứa email của user, ví dụ: _outputs/user@example.com/...)
        # if user_data["email"] not in str(file_path):
        #     raise HTTPException(status_code=403, detail="You do not have permission to access this file")

        # Kiểm tra file tồn tại
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Xác định media type dựa trên phần mở rộng file
        media_type, _ = mimetypes.guess_type(file_path) or ("application/octet-stream", None)
        if not media_type:
            media_type = "application/octet-stream"  # Fallback nếu không xác định được

        # Trả về file với media_type và filename phù hợp
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_path.name
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")