from fastapi import APIRouter
from services.ai_services import TextToVideoService as service

router = APIRouter()

# @router.post("/text-to-video/")
# def text_to_video(script: str):
#     """
#     Chuyển văn bản thành video bằng AI
#     """
#     return {"message" : "Chưa làm"}
