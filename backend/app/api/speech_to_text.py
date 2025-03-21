from fastapi import APIRouter, UploadFile, File
from services.ai_service import AIService

router = APIRouter()

@router.post("/stt/")
def speech_to_text(file: UploadFile = File(...)):
    """
    Nhận file audio và chuyển thành văn bản
    """
    # text = AIService.speech_to_text(file)
    # return {"text": text}
    return {"message" : "Chưa làm"}
