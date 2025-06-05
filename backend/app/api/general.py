from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from backend.app.services.authentication_and_authorization import verify_user_access_token
router = APIRouter()

# API trả về trang chủ của web
@router.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything"}

@router.get("/get-output/{filename:path}")
async def serve_audio(filename: str, request: Request):
    """ Lấy các file sản phẩm của AI """
    try:
        # Remember, always authentication and authorization first (zero trust)
        verify_user_access_token(source="header", request=request)

        file_path = Path(filename)
        if not str(file_path).startswith("_outputs/"):
            raise HTTPException(status_code=403, detail="Access to files outside _output directory is forbidden")
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=str(file_path),
            media_type="audio/mpeg",
            filename=file_path.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to serve audio file")