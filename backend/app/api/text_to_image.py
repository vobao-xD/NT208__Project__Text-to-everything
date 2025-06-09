from fastapi import APIRouter,Depends
from services.ai_services import TextToImageService as service
from db import schemas
from db.models import Request,Generator
from db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import insert

router = APIRouter()

@router.post("/")
def text_to_image(prompt: schemas.TTIPrompt) -> dict[str, str]:
    """
    Chuyển văn bản thành hình ảnh bằng AI (nhanh)
    """
    image = service.textToImage(prompt)
    # db: Session= Depends(get_db)
    # db.execute(insert())
    if image.startswith("Error "):
        return {"Error": image.removeprefix("Error ")}
    return {"image_url" : image}

    
