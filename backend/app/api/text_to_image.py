from fastapi import APIRouter
from services.ai_services import TextToImageService as service

router = APIRouter()

@router.post("/text-to-image-quick/")
def text_to_image(prompt: str):
    """
    Chuyển văn bản thành hình ảnh bằng AI (nhanh)
    """
    image = service.textToImageQuick(prompt)
    return {"image_base64" : image}

@router.post("text-to-image-slow")
def text_to_image(prompt: str):
    """
    Chuyển văn bản thành hình ảnh bằng AI (chậm)
    """
    image = service.getImageSlow(prompt)
    return {"image_base64" : image}
    