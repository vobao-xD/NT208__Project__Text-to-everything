from fastapi import APIRouter, UploadFile, File
from services.ai_services import SpeechToTextService as service
from db import schemas

router = APIRouter()

# @router.post("/stt/")
# def speech_to_text(file: UploadFile = File(...)):
#     """
#     Nhận file audio và chuyển thành văn bản
#     """
#     return {"message" : "Chưa làm"}
