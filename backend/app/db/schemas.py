from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, validator, Field, HttpUrl
from fastapi import UploadFile, File, Form

#################### Authentication ####################

class UserBase(BaseModel):
    email: str
    name: str
    avatar: Optional[HttpUrl] = None
    provider: str
    role: str

#################### Text to image ####################

class TTIPrompt(BaseModel):
    prompt: str
    steps: int | None = None

#################### Text to speech ####################

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")
    language: str = Field(default="Tiếng Việt", description="Language for TTS")
    gender: str = Field(..., pattern="^(male|female)$", description="Voice gender")
    style: str = Field(default="default", description="Voice style")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        if v not in ['Tiếng Việt', 'Vietnamese', 'Tiếng Anh', 'English']:
            raise ValueError("Only Vietnamese and English languages are supported")
        return v

class TTSUploadRequest(BaseModel):
    file: Optional[UploadFile] = File(None, description="Audio file (WAV, MP3, FLAC, OGG). Required if use_existing_reference is false."),
    prompt: str = Form(..., min_length=1, max_length=1000, description="Text to convert to speech"),
    language: str = Form(default="Tiếng Việt", description="Language for TTS"),
    use_existing_reference: bool = Form(False, description="Set to true to use previously uploaded reference audio"),
    @validator('use_existing_reference')
    def validate_boolean(cls, v):
        if not isinstance(v, bool):
            raise ValueError("use_existing_reference must be a boolean (True/False)")
        return v

class TTSResponse(BaseModel):
    success: bool
    file_path: str
    cost: int
    timestamp: str

#################### Text to video ####################

class TextToVideoRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    guidance_scale: float = 5.0
    fps: int = 16
    steps: int = 30
    seed: int = 123456
    frames: int = 64

#################### Speech to text ####################

class PermissionCheckRequest(BaseModel):
    permissions: List[str]

class PermissionResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str

#################### Tu tu ####################

    
class TextInput(BaseModel):
    user_text: str

class ChatRequest(BaseModel):
    prompt: str

#################### Text to Code ####################

class TTCRequest(BaseModel):
    prompt: str