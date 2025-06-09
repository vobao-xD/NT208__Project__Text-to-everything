from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID
from enum import Enum
from fastapi import UploadFile

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

class TTSClientRequest(BaseModel):
    text: str
    voice: str = "banmai"
    speed: str = "0"

class RequestBase(BaseModel):
    input_type: str  # text, audio, filee
    input_text: Optional[str] = None
    input_audio_url: Optional[str] = None
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
    output_url: HttpUrl
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

#################### Tu tu ####################

    
class TextInput(BaseModel):
    user_text: str
    max_tokens: Optional[int] = 150
class ChatRequest(BaseModel):
    prompt: str

#################### Text to Code ####################

class TTCRequest(BaseModel):
    prompt: str

#################### Payment ####################
class PaymentRequest(BaseModel):
    amount: int
    email: str
    plan: str
    billing_cycle: str = Field(alias="billingCycle")
    current_role: str = Field(alias="currentRole")
    current_billing_cycle: str = Field(alias="currentBillingCycle")
class UserSubscription(BaseModel):
    role: str
    billingCycle: Optional[str] = "monthly"

#################### Advanced Model ####################
class TextToCodeRequest(BaseModel):
    prompt:str
    language:Optional[str] = "python"
    max_tokens:Optional[int] = 150

class TextToImageRequest(BaseModel):
    model: Optional[str]="dall-e-3"
    prompt: str
    n: Optional[int] = 1
    size: Optional[str] = "1024x1024" # DALL-E 3 supports 1024x1024, 1792x1024, or 1024x1792
    quality: Optional[str] = "standard" # "standard" or "hd" for DALL-E 3
    style: Optional[str] = "vivid" # "vivid" or "natural" for DALL-E 3
    response_format: Optional[str] = "url" # "url" or "b64_json"


class TextToAudioRequest(BaseModel):
    text: str
    voice: Optional[str] = "alloy" # Example default voice
    model: Optional[str] = "gpt-4o-mini-tts"
    response_format: Optional[str] = "mp3" # e.g., mp3, opus, aac, flac, wav, pcm
    speed: Optional[float] = 1.0 # Speed of speech, 0.25 to 4.0
    # 'instructions' for gpt-4o-mini-tts, e.g., "Speak in a cheerful tone."
    instructions: Optional[str] = None

class GenerateAnswerRequest(BaseModel):
    question: str
    context: Optional[str] = None
    max_tokens: Optional[int] = 500

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatbotContentRequest(BaseModel):
    history: List[ChatMessage] = []
    user_input: str
    system_prompt: Optional[str] = "You are a helpful and friendly chatbot."
    max_tokens: Optional[int] = 500

class EnhanceTextRequest(BaseModel):
    text: str
    instruction: str 
    max_tokens: Optional[int] = 1000 

class RunwayTextToVideoRequest(BaseModel):
    prompt_text: str = Field(..., example="A majestic eagle soaring over snow-capped mountains.")
    prompt_image_url: str = Field(..., description="URL of the initial image to guide video generation.", example="https://example.com/your-image.png")
    model: Optional[str] = Field("gen4_turbo", description="RunwayML model to use (e.g., gen4_turbo, gen3a_turbo).", example="gen4_turbo")
    ratio: Optional[str] = Field("1280:720", description="Aspect ratio of the output video.", example="16:9") 
    duration: Optional[int] = Field(5, description="Duration of the video in seconds (e.g., 5 or 10).", example=5)
    seed: Optional[int] = Field(None, description="Seed for generation for reproducibility.")

class AnalyzeRequest(BaseModel):
    text: str = None
    image_url: str = None
    file: UploadFile=None

class RequestAdvancedModel(BaseModel):
    text :str=None
    image_url:str=None
    file: UploadFile=None


class FileTextToAnswerResponse(BaseModel):
    answer: str = Field(description="The answer generated by the AI based on the file and text query.")
    processed_by: str = Field(description="Indicates which AI method was used: 'vision_model' or 'assistant_file_search'.")
    file_details: Dict[str, Any] = Field(description="Details of the processed file (filename, content_type, size).")
    model_used: Optional[str] = Field(None, description="The specific AI model that generated the answer.")
    usage: Optional[Dict[str, Any]] = Field(None, description="Token usage statistics from the OpenAI API call.")


###################### Chat Detail ######################

class InputType(str,Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    file = "file"

class ChatDetailBase(BaseModel):
    input_type: InputType
    text_prompt: Optional[str] = None
    input_file_name: Optional[str] = None

    output_type: Optional[str] = None
    output_text: Optional[str] = None
    output_url: Optional[HttpUrl] = None

class ChatDetailCreate(ChatDetailBase):
    generator_id: UUID 

class ChatDetailResponse(ChatDetailBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

##################### Chat History #####################

class ChatHistoryBase(BaseModel):
    pass  

class ChatCreate(ChatHistoryBase):
    details: List[ChatDetailCreate]
    
class ChatHistoryResponse(ChatHistoryBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    details: List[ChatDetailResponse] = []

    class Config:
        from_attributes = True

class userInfo(BaseModel):
    email:str
    role:str
    expire:datetime