from PIL import Image
from fastapi import APIRouter, UploadFile, File,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytesseract
import speech_recognition as sr
import io
from moviepy import VideoFileClip
import PyPDF2
import docx
from db.schemas import *
from services.analyzeInput import guess_ai_intent
import speech_recognition as sr
from pydub import AudioSegment
import os
import uuid
import fitz

router = APIRouter()

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# === 1. Chuẩn hóa đầu vào sang văn bản ===
@router.post("/input/text")
async def input_text(text: str):
    return {"text": text}
# 2. Chuyển speech qua text
@router.post("/input/speech")
async def speech_to_text(file: UploadFile = File(...)):
    
    ext = file.filename.split(".")[-1].lower()
    input_path = f"temp_{uuid.uuid4()}.{ext}"
    output_path = input_path.replace(ext, "wav")

    
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        
        if ext == "mp3" and file.content_type == "audio/mpeg":
            audio = AudioSegment.from_file(input_path, format="mp3")
            audio.export(output_path, format="wav")
        elif ext == "wav" and file.content_type == "audio/wav":
            output_path = input_path
        else:
            return {"error": "Chỉ hỗ trợ file .mp3 hoặc .wav"}

        
        recognizer = sr.Recognizer()
        with sr.AudioFile(output_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="vi-VN")

    except Exception as e:
        return {"error": f"Lỗi xử lý: {str(e)}"}
    finally:
        # Xoá file tạm
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

    return {"text": text}

# 3. Chuyển image sang text
@router.post("/input/image")
async def input_image(file: UploadFile = File(...)):
    # Kiểm tra định dạng file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File phải là hình ảnh")
    
    try:
        # Đọc nội dung file hình ảnh
        contents = await file.read()
        # Sử dụng Image.open từ PIL để mở hình ảnh
        image = Image.open(io.BytesIO(contents))
        
        # Trích xuất văn bản từ hình ảnh
        extracted_text = pytesseract.image_to_string(image, lang="eng+vie")  # Hỗ trợ tiếng Anh và tiếng Việt
        
        # Kiểm tra nếu không trích xuất được văn bản
        if not extracted_text.strip():
            return {"text": "Không thể trích xuất văn bản từ hình ảnh"}
        
        return {"text": extracted_text.strip()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xử lý hình ảnh: {str(e)}")


# 4. Chuyển âm thanh của video sang text
@router.post("/input/video")
async def input_video(file: UploadFile = File(...)):
    video_path_name = f"temp_{uuid.uuid4()}"
    with open(f"{video_path_name}.mp4", "wb") as f:
        f.write(await file.read())

    video = VideoFileClip(f"{video_path_name}.mp4")
    audio_path = f"{video_path_name}.wav"
    video.audio.write_audiofile(audio_path)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
    except:
        text = "[Không nhận diện được giọng nói từ video]"
    finally:
        for ext in [".mp4",".wav"]:
            if os.path.exists(video_path_name + ext):
                os.remove(video_path_name + ext)
    return {"text": text}

# 5. Chuyển text trong file ra text
@router.post("/input/document")
async def input_file(file: UploadFile = File(...)):
    filename = file.filename
    extension = filename.split(".")[-1].lower()

    try:
        if extension == "txt":
            content = await file.read()
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                text = content.decode("latin-1")
        elif extension == "pdf":
            text = extract_text_from_pdf(file)
        elif extension == "docx":
            text = extract_text_from_docx(file)
        else:
            return JSONResponse(status_code=400, content={"error": "File type not supported."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    return {"text": text}

def extract_text_from_pdf(file: UploadFile):
    file.file.seek(0)
    with fitz.open(stream=file.file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def extract_text_from_docx(file: UploadFile):
    file.file.seek(0)
    doc = docx.Document(io.BytesIO(file.file.read()))
    return "\n".join(p.text for p in doc.paragraphs)

# 6. Phân tích yêu cầu của người dùng
@router.post("/analyze")
async def analyze_text(input: TextInput):
    result = guess_ai_intent(input.user_text)
    return {"intent_analysis": result}

