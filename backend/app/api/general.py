import mimetypes
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from services.history_and_output_manager import HistoryAndOutputManager
from services.authentication_and_authorization import get_current_user
router = APIRouter()

# API trả về trang chủ của web
@router.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything"}

@router.get("/get-output/{filename:path}")
async def serve_output_file(
    filename: str,
    # Bỏ comment nếu bạn cần xác thực user ở đây
    # request: Request
):
    """
    Lấy các file sản phẩm của AI (audio, image, video, text, v.v.) từ thư mục _outputs/.
    """
    try:
        # =================== PHẦN SỬA LỖI LOGIC ===================

        # 1. Lấy đường dẫn tuyệt đối, an toàn của thư mục _outputs
        #    .resolve() để đảm bảo đường dẫn là tuyệt đối và tránh lỗi
        outputs_dir = Path("_outputs").resolve()

        # 2. Tạo đường dẫn đầy đủ đến file được yêu cầu một cách an toàn
        #    Bằng cách này, `filename` sẽ được coi là tương đối so với `outputs_dir`
        full_path = outputs_dir.joinpath(filename).resolve()

        # 3. Kiểm tra bảo mật: Đảm bảo đường dẫn cuối cùng thực sự nằm BÊN TRONG `outputs_dir`
        #    Đây là cách kiểm tra đúng để chống lại tấn công Path Traversal (ví dụ: `../`)
        if not str(full_path).startswith(str(outputs_dir)):
            raise HTTPException(status_code=403, detail="Access to files outside _outputs directory is forbidden")

        # =========================================================

        # Kiểm tra file tồn tại
        if not full_path.is_file(): # Dùng is_file() để chắc chắn nó là file
            raise HTTPException(status_code=404, detail="File not found")

        # Xác định media type dựa trên phần mở rộng file
        media_type, _ = mimetypes.guess_type(full_path)
        if not media_type:
            media_type = "application/octet-stream"

        # Trả về file với đường dẫn đầy đủ đã được xác thực
        return FileResponse(
            path=str(full_path),
            media_type=media_type,
            filename=full_path.name
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to serve file: {str(e)}")
    
@router.post("/save-output-file")
async def save_output_file_endpoint(
    user_email: str,
    generator_name: str,
    file_content: List[int],  # Nhận mảng bytes từ frontend
    file_extension: str,
    current_user=Depends(get_current_user)
):
    if current_user.email != user_email:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    file_bytes = bytes(file_content)  # Chuyển mảng bytes thành bytes
    save_path = HistoryAndOutputManager.save_output_file(user_email, generator_name, file_bytes, file_extension)
    return {"file_path": str(save_path)}