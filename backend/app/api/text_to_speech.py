import re
from fastapi import APIRouter, HTTPException, Depends
from services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse
from services.authentication_and_authorization import Auth
import httpx
from sqlalchemy.orm import Session
from db import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter()

@router.post("/default", response_model=TTSResponse)
async def text_to_speech_default(
    request: TTSRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Gọi API viXTTS để tạo âm thanh từ văn bản với giọng mặc định.
    """
    try:
        token = credentials.credentials
        return await service.text_to_speech_with_default_voice(
            request, token, db
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")