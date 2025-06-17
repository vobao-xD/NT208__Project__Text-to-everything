from datetime import time, timedelta
from PIL import Image
from fastapi import APIRouter, Depends, Request, UploadFile, File,HTTPException,status,Header
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from pydantic import BaseModel
import pytesseract
import speech_recognition as sr
import io
from moviepy import VideoFileClip
import PyPDF2
import docx
from services.authentication_and_authorization import verify_user_access_token
from services.history_and_output_manager import HistoryAndOutputManager
from db.schemas import *
from services.input_analyzer import guess_ai_intent
import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid
import fitz
from redis import asyncio as aioredis
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
REDIS_URL=os.getenv("REDIS_URL")
TESSERACT_PATH=os.getenv("TESSERACT_PATH")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_text_from_pdf(file: UploadFile):
    file.file.seek(0)
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(file: UploadFile):
    file.file.seek(0)
    doc = docx.Document(io.BytesIO(file.file.read()))
    return "\n".join(p.text for p in doc.paragraphs)

# 1. Chuẩn hóa đầu vào sang văn bản
@router.post("/input/text")
async def input_text(request: Request, text: str):
    user_data = verify_user_access_token(source="cookie", request=request)
    return {"text": text}

# 2. Chuyển speech qua text
@router.post("/input/speech")
async def speech_to_text(
    request: Request,
    file: UploadFile = File(...)
    ):
    user_data = verify_user_access_token(source="cookie", request=request)

    ext = file.filename.split(".")[-1].lower()
    input_bytes = await file.read()
    input_path = f"temp_{uuid.uuid4()}.{ext}"
    output_path = input_path.replace(ext, "wav")

    # Lưu file upload tạm thời để xử lý
    with open(input_path, "wb") as f:
        f.write(input_bytes)

    try:
        if ext == "mp3" and file.content_type == "audio/mpeg":
            audio = AudioSegment.from_file(input_path, format="mp3")
            audio.export(output_path, format="wav")
        elif ext == "wav" and file.content_type == "audio/wav":
            output_path = input_path
        else:
            os.remove(input_path)
            return {"error": "Chỉ hỗ trợ file .mp3 hoặc .wav"}

        recognizer = sr.Recognizer()
        with sr.AudioFile(output_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="vi-VN")

        # Lưu file wav output vào _outputs
        with open(output_path, "rb") as f:
            wav_bytes = f.read()
        save_path = HistoryAndOutputManager.save_output_file(
            user_email=user_data["email"],
            generator_name="speech_to_text",
            file_content=wav_bytes,
            file_extension="wav"
        )
    except Exception as e:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path) and output_path != input_path:
            os.remove(output_path)
        return {"error": f"Lỗi xử lý: {str(e)}"}
    # Xoá file tạm
    if os.path.exists(input_path):
        os.remove(input_path)
    if os.path.exists(output_path) and output_path != input_path:
        os.remove(output_path)

    return {"text": text, "file_path": str(save_path)}

# 3. Chuyển image sang text
@router.post("/input/image")
async def input_image(request: Request, file: UploadFile = File(...)):
    user_data = verify_user_access_token(source="cookie", request=request)
    # Kiểm tra định dạng file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là hình ảnh")
    try:
        # Đọc nội dung file hình ảnh
        contents = await file.read()
        # Lưu file ảnh gốc vào _outputs
        save_path = HistoryAndOutputManager.save_output_file(
            user_email=user_data["email"],
            generator_name="image_to_text",
            file_content=contents,
            file_extension=file.filename.split(".")[-1].lower()
        )
        # Sử dụng Image.open từ PIL để mở hình ảnh
        image = Image.open(io.BytesIO(contents))
        # Trích xuất văn bản từ hình ảnh
        extracted_text = pytesseract.image_to_string(image, lang="eng+vie")  # Hỗ trợ tiếng Anh và tiếng Việt
        # Kiểm tra nếu không trích xuất được văn bản
        if not extracted_text.strip():
            return {"text": "Không thể trích xuất văn bản từ hình ảnh", "file_path": str(save_path)}
        return {"text": extracted_text.strip(), "file_path": str(save_path)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý hình ảnh: {str(e)}")

# 4. Chuyển âm thanh của video sang text
@router.post("/input/video")
async def input_video(
    request: Request,
    file: UploadFile = File(...)   
    ):
    user_data = verify_user_access_token(source="cookie", request=request)

    ext = file.filename.split(".")[-1].lower()
    video_bytes = await file.read()
    video_temp_path = f"temp_{uuid.uuid4()}.{ext}"
    audio_temp_path = video_temp_path.replace(ext, "wav")

    # Lưu file video gốc vào _outputs
    video_save_path = HistoryAndOutputManager.save_output_file(
        user_email=user_data["email"],
        generator_name="video_to_text",
        file_content=video_bytes,
        file_extension=ext
    )

    # Lưu file video tạm để xử lý
    with open(video_temp_path, "wb") as f:
        f.write(video_bytes)

    try:
        video = VideoFileClip(video_temp_path)
        video.audio.write_audiofile(audio_temp_path)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_temp_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="vi-VN")
        # Lưu file audio vào _outputs
        with open(audio_temp_path, "rb") as f:
            audio_bytes = f.read()
        audio_save_path = HistoryAndOutputManager.save_output_file(
            user_email=user_data["email"],
            generator_name="video_to_text_audio",
            file_content=audio_bytes,
            file_extension="wav"
        )
    except Exception as e:
        if os.path.exists(video_temp_path):
            os.remove(video_temp_path)
        if os.path.exists(audio_temp_path):
            os.remove(audio_temp_path)
        return {"error": f"Lỗi xử lý: {str(e)}"}
    # Xoá file tạm
    if os.path.exists(video_temp_path):
        os.remove(video_temp_path)
    if os.path.exists(audio_temp_path):
        os.remove(audio_temp_path)

    return {"text": text, "video_file_path": str(video_save_path), "audio_file_path": str(audio_save_path)}

# 5. Chuyển text trong file ra text
@router.post("/input/document")
async def input_file(request: Request, file: UploadFile = File(...)):
    user_data = verify_user_access_token(source="cookie", request=request)
    filename = file.filename
    extension = filename.split(".")[-1].lower()
    file_bytes = await file.read()
    # Lưu file document gốc vào _outputs
    save_path = HistoryAndOutputManager.save_output_file(
        user_email=user_data["email"],
        generator_name="document_to_text",
        file_content=file_bytes,
        file_extension=extension
    )
    try:
        if extension == "txt":
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1")
        elif extension == "pdf":
            # Tạo lại file-like object cho extract_text_from_pdf
            file.file = io.BytesIO(file_bytes)
            text = extract_text_from_pdf(file)
        elif extension == "docx":
            file.file = io.BytesIO(file_bytes)
            text = extract_text_from_docx(file)
        else:
            return JSONResponse(status_code=400, content={"error": "File type not supported.", "file_path": str(save_path)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e), "file_path": str(save_path)})
    return {"text": text, "file_path": str(save_path)}

# 6. Phân tích yêu cầu của người dùng
@router.post("/analyze")
async def analyze_text(
    input: TextInput,
    request: Request
):
    """
    Phân tích intent của người dùng. Giới hạn 10 lượt/ngày cho role 'free'.
    """
    redis_client = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    user_data = verify_user_access_token(source="cookie", request=request)

    if user_data["role"] == "free":
        current_time = datetime.now()
        today = current_time.date()
        tomorrow = today + timedelta(days=1)
        end_of_today_timestamp = int(datetime.combine(tomorrow, time.min).timestamp())

        analyze_count_key = f"analyze_count:{today.isoformat()}:{user_data.get('email')}"

        used_calls = await redis_client.incr(analyze_count_key)

        if used_calls == 1: 
            await redis_client.expireat(analyze_count_key, end_of_today_timestamp)
        
        if used_calls > 10: # Dùng "> 10" vì đã incr trước đó
            await redis_client.decr(analyze_count_key)
            
            retry_after_seconds = max(0, end_of_today_timestamp - int(current_time.timestamp()))
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Bạn đã sử dụng hết lượt gọi miễn phí. Vui lòng nâng cấp tài khoản để sử dụng thêm.",
                headers={"Retry-After": str(int(retry_after_seconds))} # Thêm header Retry-After
            )
    
    # Logic xử lý chính
    result = guess_ai_intent(input.user_text)
    return {"intent_analysis": result}

