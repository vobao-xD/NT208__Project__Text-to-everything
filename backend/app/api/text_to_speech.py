from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from services.authentication_and_authorization import verify_user_access_token
from services import TextToSpeechService as service
from db.schemas import TTSRequest, TTSResponse
from typing import Optional

router = APIRouter()

@router.post("/default", response_model = TTSResponse)
async def text_to_speech_default(
    request: Request,
    TTS_request: TTSRequest
):
    """
    Gọi API viXTTS (tự tạo) để tạo âm thanh từ văn bản với giọng mặc định.
    """
    try:
        # Hàm verify_user_access_token sẽ trả về dict chứa email, role, exp.
        # Truy cập các thuộc tính bằng cách user_data["{tên thuộc tính}"]
        # Ví dụ: email = user_data["email"]
        # Đọc code để hiểu hàm hoạt động thế nào
        user_data = verify_user_access_token(source="cookie", request=request)
        return await service.text_to_speech_with_default_voice(user_data, TTS_request)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")
    
@router.post("/custom", response_model = TTSResponse)
async def custom_text_to_speech_with_voice_cloning(
    request: Request,
    file: Optional[UploadFile] = File(None),
    text: str = Form(..., min_length=1, max_length=1000),
    language: str = Form(default="Tiếng Việt"),
    use_existing_reference: bool = Form(False)
):
    """
    Gọi API viXTTS với chức năng voice cloning từ một file âm thanh người dùng tải lên
    """
    try:
        user_data = verify_user_access_token(source="cookie", request=request)
        return await service.text_to_speech_with_custom_voice(user_data, text, language, use_existing_reference, file)  
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi không xác định: {str(e)}")

