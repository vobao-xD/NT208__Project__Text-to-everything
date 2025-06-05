from fastapi import APIRouter, Depends, HTTPException, Request
from requests import Session
from backend.app.db.database import get_db
from services.authentication_and_authorization import verify_user_access_token
from services.text_to_video import TextToVideoService as service
from fastapi.responses import StreamingResponse
from db.schemas import TextToVideoRequest
import io

router = APIRouter()

@router.post("/")
def text_to_video(
    request: Request,
    prompt: TextToVideoRequest,
    db: Session = Depends(get_db)
):
    user_data = verify_user_access_token(source="header", request=request)
    try:
        prompt_dict = prompt.model_dump()

        # Dịch prompt
        translated_prompt = service.translateText(prompt_dict["prompt"])
        prompt_dict["prompt"] = translated_prompt

        # Gửi request tới API 
        video_bytes = service.textToVideo(prompt_dict)

        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/mp4",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
