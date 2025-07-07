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
    request: Request
):
    """
    Lấy các file sản phẩm của AI (audio, image, video, text, v.v.) từ thư mục _outputs/.
    """
    try:

        outputs_dir = Path("_outputs").resolve()
        full_path = outputs_dir.joinpath(filename).resolve()
        if not str(full_path).startswith(str(outputs_dir)):
            raise HTTPException(status_code=403, detail="Access to files outside _outputs directory is forbidden")

        if not full_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")

       
        media_type, _ = mimetypes.guess_type(full_path)
        if not media_type:
            media_type = "application/octet-stream"

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
    file_content: List[int],  
    file_extension: str,
    current_user=Depends(get_current_user)
):
    if current_user.email != user_email:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    file_bytes = bytes(file_content)  # Chuyển mảng bytes thành bytes
    save_path = HistoryAndOutputManager.save_output_file(user_email, generator_name, file_bytes, file_extension)
    return {"file_path": str(save_path)}