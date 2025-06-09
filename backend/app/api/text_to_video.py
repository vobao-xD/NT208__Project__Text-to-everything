from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from services.text_to_video import TextToVideoService as service
from db.schemas import TextToVideoRequest
import io

router = APIRouter()

@router.post("/")
def text_to_video(prompt: TextToVideoRequest):
    try:
        # Convert model sang dict
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
