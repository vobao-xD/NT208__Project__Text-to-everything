from fastapi import APIRouter
from services.ai_service import AIService

router = APIRouter()

@router.post("/text-to-image/")
def text_to_image(prompt: str):
    """
    Chuyển văn bản thành hình ảnh bằng AI
    """
    # image_url = AIService.text_to_image(prompt)
    # return {"image_url": image_url}
    pass

