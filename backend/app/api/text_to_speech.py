from fastapi import APIRouter
from services.ai_services import TextToSpeechService as service

router = APIRouter()

@router.post("/")
def text_to_speech(text: str, voice: str = "banmai", speed: str = "0"):
    """
    Chuyển văn bản thành giọng nói
    """
    audio_url = service.text_to_speech(text, voice, speed)
    return {"audio_url": audio_url} 