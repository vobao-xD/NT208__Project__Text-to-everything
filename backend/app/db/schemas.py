from pydantic import BaseModel
from datetime import datetime

#################### Authentication ####################


#################### Text to image ####################

class SlowPrompt(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    height: int | None = None
    width: int | None = None
    num_steps: int | None = None
    guidance: float | None = None
    model: int | None = None

class QuickPrompt(BaseModel):
    prompt: str
    steps: int | None = None

#################### Text to speech ####################

class TTSClientRequest(BaseModel):
    text: str
    voice: str = "banmai"
    speed: str = "0"

class RequestBase(BaseModel):
    input_type: str  # text, audio, file
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

#################### Speech to text ####################
