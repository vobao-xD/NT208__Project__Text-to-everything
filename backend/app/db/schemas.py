from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

#################### Authentication ####################


#################### Text to image ####################



class TTIPrompt(BaseModel):
    prompt: str
    steps: int | None = None

#################### Text to speech ####################

class TTSClientRequest(BaseModel):
    text: str
    voice: str = "banmai"
    speed: str = "0"

class RequestBase(BaseModel):
    input_type: str  # text, audio, filee
    input_text: str | None = None
    input_audio_url: str | None = None
    output_type: str  # speech, image, video

class RequestCreate(RequestBase):
    pass

class RequestResponse(RequestBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ResponseBase(BaseModel):
    output_type: str
    output_url: str
    model_used: str

class ResponseCreate(ResponseBase):
    pass

class ResponseResponse(ResponseBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True

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