import re
from fastapi import APIRouter, HTTPException, Depends
from services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse
from services.authentication_and_authorization import Auth
import httpx
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter()

@router.post("/text-to-speech/default", response_model=TTSResponse)
async def _(request: TTSRequest, token: str, db: Session = Depends(get_db)):
    return service.text_to_speech_with_default_voice(request, token, db)
