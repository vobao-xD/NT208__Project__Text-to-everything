import re
from services.authentication_and_authorization import verify_user_access_token
from fastapi import APIRouter, File, Form, HTTPException, Depends, Request, UploadFile
from services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse, TTSUploadRequest
from typing import Optional
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pathlib import Path
from db import get_db
import logging

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
    file: Optional[UploadFile] = File(None),
    text: str = Form(..., min_length=1, max_length=1000),
    language: str = Form(default="Tiếng Việt"),
    use_existing_reference: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Gọi API viXTTS với chức năng voice cloning từ một file âm thanh người dùng tải lên
    """
    try:
        user_data = verify_user_access_token(request)
        return await service.text_to_speech_with_custom_voice(db, user_data, text, language, use_existing_reference, file)  
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
