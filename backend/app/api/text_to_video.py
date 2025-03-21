from fastapi import APIRouter
from services.ai_service import AIService

router = APIRouter()

@router.post("/text-to-video/")
def text_to_video(script: str):
    """
    Chuyển văn bản thành video bằng AI
    """
    # video_url = AIService.text_to_video(script)
    # return {"video_url": video_url}
    pass
