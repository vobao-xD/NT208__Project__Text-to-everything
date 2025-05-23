from fastapi import APIRouter
from services.ai_services import TextToImageService as service
from db import schemas

router = APIRouter()

@router.post("/")
def text_to_image(prompt: schemas.TTIPrompt):
    """
    Chuyển văn bản thành hình ảnh bằng AI (nhanh)
    """
    image = service.textToImage(prompt)
    return {"image_url" : image}

    
