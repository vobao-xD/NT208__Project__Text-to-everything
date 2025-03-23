from pydantic import BaseModel
from datetime import datetime

#################### Text to image ####################

class SlowPrompt(BaseModel):
    prompt: str
    negative_prompt: str
    height: int
    width: int
    num_steps: int
    guidance: float
    model: int

class QuickPrompt(BaseModel):
    prompt: str
    steps: int


#################### Text to speech ####################

from pydantic import BaseModel
from datetime import datetime

class RequestBase(BaseModel):
    input_type: str  # text, audio, file
    input_text: str | None = None
    input_audio_url: str | None = None
    output_type: str  # speech, image, video

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

class ResponseResponse(ResponseBase):
    id: int
    request_id: int
    created_at: datetime

    class Config:
        from_attributes = True

#################### Text to video ####################

#################### Speech to text ####################
