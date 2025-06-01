import re
from fastapi import APIRouter, HTTPException
from services.ai_services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse
from backend.app.services.auth_service import Auth
import httpx

router = APIRouter()

def extract_audio_text(text: str) -> str:
    match = re.search(r"['\"](.*?)['\"]", text)
    if match:
        return match.group(1)
    return text  

@router.post("/text-to-speech/default", response_model=TTSResponse)
async def _(request: TTSRequest):
    return service.text_to_speech_with_default_voice(request)
