from fastapi import APIRouter
from services.ai_services import TextToSpeechService as service
from db import schemas

router = APIRouter()

@router.post("/")
def text_to_speech(prompt: schemas.TTSClientRequest):
    """
    Chuyển văn bản thành giọng nói
    """
    audio_url = service.text_to_speech(prompt.text, prompt.voice, prompt.speed)
    return {"audio_url": audio_url}  