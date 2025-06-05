from fastapi import APIRouter, Request, Depends
from services.authentication_and_authorization import verify_user_access_token
from services import TextToImageService as service
from db import get_db
from db.schemas import TTIPrompt, TTIResponse
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("/", response_model=TTIResponse)
def text_to_image(
    request: Request, 
    prompt: TTIPrompt,
    db: Session = Depends(get_db)
):
    """
    Chuyển văn bản thành hình ảnh bằng AI
    """
    try:
        user_data = verify_user_access_token(source="header", request=request)
        return service.textToImage(prompt, user_data, db)
    except Exception as e:
        return e
