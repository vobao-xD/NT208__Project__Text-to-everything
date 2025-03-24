from fastapi import APIRouter
from services.ai_services import TextToImageService as service
from db import schemas

router = APIRouter()

@router.post("/quick")
def text_to_image(prompt: schemas.QuickPrompt):
    """
    Chuyển văn bản thành hình ảnh bằng AI (nhanh)
    """
    image = service.textToImageQuick(prompt)
    return {"image_base64" : image}

@router.post("/slow")
def text_to_image(prompt: schemas.SlowPrompt):
    """
    Chuyển văn bản thành hình ảnh bằng AI (chậm)
    """
    image = service.textToImageSlow(prompt)
    return {"image_base64" : image}
    
