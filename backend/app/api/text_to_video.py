from fastapi import APIRouter, HTTPException, Request
from services.authentication_and_authorization import verify_user_access_token
from services.text_to_video import TextToVideoService as service
from db.schemas import TextToVideoRequest, TTVResponse

router = APIRouter()

@router.post("/", response_model=TTVResponse)
def text_to_video(
    request: Request,
    prompt: TextToVideoRequest
):
    user_data = verify_user_access_token(source="cookie", request=request)
    try:
        prompt_dict = prompt.model_dump()

        # Dịch prompt
        translated_prompt = service.translateText(prompt_dict["prompt"])
        prompt_dict["prompt"] = translated_prompt

        # Gửi request tới API 
        return service.textToVideo(user_data, prompt_dict)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
