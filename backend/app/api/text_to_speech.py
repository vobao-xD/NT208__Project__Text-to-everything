import re
from services.authentication_and_authorization import verify_user_access_token
from fastapi import APIRouter, HTTPException, Depends, Request
from services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse, TTSUploadRequest
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pathlib import Path
from db import get_db

router = APIRouter()

@router.post("/default", response_model = TTSResponse)
async def text_to_speech_default(
    request: Request,
    TTS_request: TTSRequest,
    db: Session = Depends(get_db)
):
    """
    Gọi API viXTTS (tự tạo) để tạo âm thanh từ văn bản với giọng mặc định.
    """
    try:
        user_data = verify_user_access_token(request)
        return await service.text_to_speech_with_default_voice(TTS_request, user_data, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")
    
@router.post("/custom", response_model = TTSResponse)
async def custom_text_to_speech_with_voice_cloning(
    request: Request,
    TTS_request: TTSUploadRequest,
    db: Session = Depends(get_db)
):
    """
    Gọi API viXTTS với chức năng voice cloning từ một file âm thanh người dùng tải lên
    """
    try:
        user_data = verify_user_access_token(request)
        return await service.text_to_speech_with_custom_voice(TTS_request, user_data, db) 
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")

@router.get("/get-audio/{filename:path}")
async def serve_audio(filename: str, request: Request):
    """Serve generated audio files"""
    try:
        # Remember, always authentication and authorization first (zero trust)
        verify_user_access_token(request)

        file_path = Path(filename)
        if not str(file_path).startswith("_audio_output/"):
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
