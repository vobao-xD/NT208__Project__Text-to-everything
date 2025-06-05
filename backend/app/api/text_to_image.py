from fastapi import APIRouter, Request, Depends
from services.authentication_and_authorization import verify_user_access_token
from services import TextToImageService as service
from db import get_db
from db.schemas import TTIPrompt
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/")
def text_to_image(
    request: Request, 
    prompt: TTIPrompt,
    db: Session = Depends(get_db)
):
    """
    Chuyển văn bản thành hình ảnh bằng AI
    """
    user_data = verify_user_access_token(source="header", request=request)
    image = service.textToImage(prompt, user_data, db)
    return {"image_url" : image} # image url
