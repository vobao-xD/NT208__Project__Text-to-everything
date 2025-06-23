import logging
from fastapi import APIRouter, Request
from services.authentication_and_authorization import verify_user_access_token
from services import TextToImageService as service
from db.schemas import TTIPrompt, TTIResponse

router = APIRouter()

@router.post("/", response_model=TTIResponse)
def text_to_image(
    request: Request, 
    prompt: TTIPrompt
):
    """
    Chuyển văn bản thành hình ảnh bằng AI
    """
    try:
        user_data = verify_user_access_token(source="cookie", request=request)
        return service.textToImage(user_data, prompt)
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
        return TTIResponse(success=False, file_path=str(e))
