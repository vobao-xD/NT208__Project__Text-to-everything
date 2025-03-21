from fastapi import APIRouter
from services.ai_service import AIService

router = APIRouter()

@router.post("/tts/")
def text_to_speech(text: str, voice: str = "banmai", speed: str = "0"):
    """
    Chuyển văn bản thành giọng nói
    """
    audio_url = AIService.text_to_speech(text, voice, speed)
    return {"audio_url": audio_url}