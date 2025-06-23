from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from uuid import UUID
from fastapi import UploadFile
from enum import Enum

#################### Authentication ####################

class UserBase(BaseModel):
    email: str
    name: str
    avatar: Optional[HttpUrl] = None
    provider: str = "unknown"
    role: str = "free"
    expires_at: Optional[datetime] = None

#################### Text to speech ####################

class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="Text to convert to speech")
    language: str = Field(default="Tiếng Việt", description="Language for TTS")
    gender: str = Field(..., pattern="^(male|female)$", description="Voice gender: 'male' or 'female'")
    style: str = Field(default="default", description="Voice style: depends on gender")
    
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
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female']:
            raise ValueError("Gender must be 'male' or 'female'")
        return v
    
    @validator('style')
    def validate_style(cls, v, values):
        if 'gender' not in values:
            raise ValueError("Gender must be specified before style validation")
        
        gender = values['gender']
        male_styles = ['calm', 'cham', 'nhanh', 'default']
        female_styles = ['calm', 'cham', 'luuloat', 'nhannha', 'default']
        
        allowed_styles = male_styles if gender == 'male' else female_styles
        if v not in allowed_styles:
            raise ValueError(f"Style must be one of {allowed_styles} for gender '{gender}'")
        return v

class TTSResponse(BaseModel):
    success: bool
    file_path: str

class TTSError(Exception):
    """Custom exception for TTS operations"""
    pass

#################### Text to image ####################

class TTIPrompt(BaseModel):
    prompt: str
    steps: int = 4

class TTIResponse(BaseModel):
    success: bool
    file_path: str

#################### Text to video ####################

class TextToVideoRequest(BaseModel):
    prompt: str
    negative_prompt: str | None = None
    guidance_scale: float = 5.0
    fps: int = 16
    steps: int = 30
    seed: int = 123456
    frames: int = 64

class TTVResponse(BaseModel):
    success: bool
    file_path: str

#################### Speech to text ####################

class PermissionCheckRequest(BaseModel):
    permissions: List[str]

class PermissionResult(BaseModel):
    allowed: bool
    reason: Optional[str] = None

class QuestionRequest(BaseModel):
    question: str

#################### What is this??? ####################

class TextInput(BaseModel):
    user_text: str
    max_tokens: Optional[int] = 150

class ChatRequest(BaseModel):
    prompt: str

#################### Text to Code ####################

class TTCRequest(BaseModel):
    prompt: str

class TTCResponse(BaseModel):
    success: bool
    code: str

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

###################### Chat History ######################

class InputType(str, Enum):
    text = "text"
    image = "image"
    audio = "audio"
    video = "video"
    file = "file"

class ChatDetailBase(BaseModel):
    input_type: InputType
    input_text: Optional[str] = None
    input_file_name: Optional[str] = None
    input_file_path: Optional[str] = None

    output_type: InputType
    output_text: Optional[str] = None
    output_file_name: Optional[str] = None
    output_file_path: Optional[str] = None

class ChatDetailCreate(ChatDetailBase):
    generator_id: str

class ChatDetailResponse(ChatDetailBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

##################### Chat History #####################

class ChatHistoryBase(BaseModel):
    pass

class ChatCreate(ChatHistoryBase):
    chat_details: List[ChatDetailCreate]
    
class ChatHistoryResponse(ChatHistoryBase):
    id: UUID
    user_email: str
    created_at: datetime
    chat_details: List[ChatDetailResponse] = []

    class Config:
        from_attributes = True

