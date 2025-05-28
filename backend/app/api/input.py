from PIL import Image
from fastapi import APIRouter, UploadFile, File,HTTPException
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

router = APIRouter()

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# === 1. Chuẩn hóa đầu vào sang văn bản ===
@router.post("/input/text")
async def input_text(text: str):
    return {"text": text}
# 2. Chuyển speech qua texttext
@router.post("/input/speech")
async def speech_to_text(file: UploadFile = File(...)):
    
    ext = file.filename.split(".")[-1].lower()
    input_path = f"temp_{uuid.uuid4()}.{ext}"
    output_path = input_path.replace(ext, "wav")

    
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        
        if ext == "mp3":
            audio = AudioSegment.from_file(input_path, format="mp3")
            audio.export(output_path, format="wav")
        elif ext == "wav":
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


# 4. Chuyển âm thanh của video sang texttext
@router.post("/input/video")
async def input_video(file: UploadFile = File(...)):
    with open("temp_video.mp4", "wb") as f:
        f.write(await file.read())
    video = VideoFileClip("temp_video.mp4")
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="vi-VN")
    except:
        text = "[Không nhận diện được giọng nói từ video]"
    return {"text": text}

# 5. Chuyển text trong file ra texttext
@router.post("/input/file")
async def input_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename.lower()
    text = ""
    if filename.endswith(".txt"):
        text = content.decode("utf-8")
    elif filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
    else:
        return {"error": "Unsupported file type"}
    return {"text": text}

# 6. Phân tích yêu cầu của người dùngdùng
@router.post("/analyze")
async def analyze_text(input: TextInput):
    result = guess_ai_intent(input.user_text)
    return {"intent_analysis": result}

