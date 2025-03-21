from fastapi import APIRouter, Depends
from services.ai_service import AIService
from sqlalchemy.orm import Session
from db import *

router = APIRouter()

@router.post("/tts/")
def text_to_speech(text: str, voice: str = "banmai", speed: str = "0", db: Session = Depends(get_db)):
    """
    Chuyển văn bản thành giọng nói
    """
    # audio_url = AIService.text_to_speech(text, voice, speed)
    # return {"audio_url": audio_url}
    return {"audio_url": "https://example.com/audio.mp3"}