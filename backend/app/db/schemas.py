from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID
from typing import Optional, Literal
from datetime import datetime
import re
from fastapi import File, UploadFile, Form
from uuid import UUID
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
    text: str = Form(..., min_length=1, max_length=1000, description="Text to convert to speech")
    language: str = Form(default="Tiếng Việt", description="Language for TTS")
    gender: str = Form(..., pattern="^(male|female)$", description="Voice gender: 'male' or 'female'")
    style: str = Form(default="default", description="Voice style: depends on gender")
    
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
    
class TTSUploadRequest(BaseModel):
    text: str = Form(..., min_length=1, max_length=1000, description="Text to convert to speech")
    language: str = Form(default="Tiếng Việt", description="Language for TTS")
    file: Optional[UploadFile] = File(None, description="Audio file (WAV, MP3, FLAC, OGG). Required if use_existing_reference is false.")
    use_existing_reference: bool = Form(False, description="Set to true to use previously uploaded reference audio")
    
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
    
    @validator('use_existing_reference')
    def validate_boolean(cls, v):
        if not isinstance(v, bool):
            raise ValueError("use_existing_reference must be a boolean (True/False)")
        return v

class TTSResponse(BaseModel):
    success: bool
    file_path: str

#################### Text to image ####################

class TTIPrompt(BaseModel):
    prompt: str
    steps: int | None = None

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

#################### What is this??? ####################

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

###################### Chat History ######################

# class InputType(str, Enum):
#     text = "text"
#     file = "file"

# class OutputType(str, Enum):
#     text = "text"
#     audio = "audio"
#     image = "image"
#     video = "video"

# class ChatDetailBase(BaseModel):
#     input_type: InputType = Field(..., description="Loại input: text hoặc file")
#     text_prompt: Optional[str] = Field(None, description="Nội dung text input", max_length=1000)
#     input_file_path: Optional[str] = Field(None, description="Đường dẫn file input", max_length=1024)
#     output_type: OutputType = Field(..., description="Loại output: text, audio, image, video")
#     output_content: Optional[str] = Field(None, description="Nội dung text output", max_length=10000)
#     output_file_path: Optional[str] = Field(None, description="Đường dẫn file output", max_length=1024)

#     @validator("input_type")
#     def validate_input_type(cls, v):
#         if v not in [InputType.text, InputType.file]:
#             raise ValueError("input_type phải là 'text' hoặc 'file'")
#         return v

#     @validator("output_type")
#     def validate_output_type(cls, v):
#         if v not in [OutputType.text, OutputType.audio, OutputType.image, OutputType.video]:
#             raise ValueError("output_type phải là 'text', 'audio', 'image', hoặc 'video'")
#         return v

# class ChatDetailCreate(ChatDetailBase):
#     generator_id: UUID = Field(..., description="ID của generator")

# class ChatDetailResponse(ChatDetailBase):
#     id: UUID = Field(..., description="ID của chat detail")
#     chat_history_id: UUID = Field(..., description="ID của phiên chat")
#     generator_id: UUID = Field(..., description="ID của generator")
#     created_at: datetime = Field(..., description="Thời gian tạo")

#     class Config:
#         from_attributes = True  # Ánh xạ từ model SQLAlchemy

# class ChatHistoryBase(BaseModel):
#     user_id: UUID = Field(..., description="ID của user")

# class ChatHistoryCreate(ChatHistoryBase):
#     chat_details: List[ChatDetailCreate] = Field(..., description="Danh sách chi tiết chat")

# class ChatHistoryResponse(ChatHistoryBase):
#     id: UUID = Field(..., description="ID của phiên chat")
#     created_at: datetime = Field(..., description="Thời gian tạo")
#     chat_details: List[ChatDetailResponse] = Field(default_factory=list, description="Danh sách chi tiết chat")

#     class Config:
#         from_attributes = True  # Ánh xạ từ model SQLAlchemy

# class ChatHistoryListResponse(BaseModel):
#     chat_histories: List[ChatHistoryResponse] = Field(..., description="Danh sách các phiên chat")



class ChatHistoryBase(BaseModel):
    user_id: UUID = Field(..., description="ID of the user who created the chat history")

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistoryResponse(ChatHistoryBase):
    id: UUID = Field(..., description="Unique identifier of the chat history")
    created_at: datetime = Field(..., description="Timestamp when the chat history was created")
    updated_at: datetime = Field(..., description="Timestamp when the chat history was last updated")

    class Config:
        from_attributes = True  # Allow mapping from SQLAlchemy models

class ChatDetailBase(BaseModel):
    chat_history_id: UUID = Field(..., description="ID of the associated chat history")
    input_type: Literal["text", "image", "audio", "video", "document"] = Field(
        ..., description="Type of input (e.g., text, image, audio)"
    )
    text_prompt: Optional[str] = Field(
        None, max_length=1000, description="Text input or prompt (if applicable)"
    )
    input_file_path: Optional[str] = Field(
        None, description="Path to input file (if applicable)"
    )
    output_type: Literal["text", "image", "audio", "video"] = Field(
        ..., description="Type of output (e.g., text, image, audio)"
    )
    output_content: Optional[str] = Field(
        None, max_length=1000, description="Text output (if applicable)"
    )
    output_file_path: Optional[str] = Field(
        None, description="Path to output file (if applicable)"
    )
    generator_id: UUID = Field(..., description="ID of the generator used (e.g., TTS, text-to-image)")

    @validator("text_prompt")
    def validate_text_prompt(cls, v):
        if v and not v.strip():
            raise ValueError("Text prompt cannot be empty or whitespace")
        return v.strip() if v else v

    @validator("input_file_path", "output_file_path")
    def validate_file_path(cls, v):
        if v:
            # Ensure file path is relative and starts with allowed directories
            allowed_prefixes = ["_input/", "_output/", "_audio_output/", "_temp_uploads/"]
            if not any(v.startswith(prefix) for prefix in allowed_prefixes):
                raise ValueError("File path must start with an allowed directory")
            # Basic path format validation
            if not re.match(r"^[a-zA-Z0-9_/.-]+$", v):
                raise ValueError("Invalid file path format")
        return v

class ChatDetailCreate(ChatDetailBase):
    pass

class ChatDetailResponse(ChatDetailBase):
    id: UUID = Field(..., description="Unique identifier of the chat detail")
    created_at: datetime = Field(..., description="Timestamp when the chat detail was created")
    updated_at: datetime = Field(..., description="Timestamp when the chat detail was last updated")

    class Config:
        from_attributes = True  # Allow mapping from SQLAlchemy models

class ChatHistoryListResponse(BaseModel):
    histories: list[ChatHistoryResponse] = Field(
        ..., description="List of chat histories for the user"
    )

class ChatHistoryDetailResponse(BaseModel):
    history: ChatHistoryResponse = Field(..., description="Chat history details")
    details: list[ChatDetailResponse] = Field(
        ..., description="List of chat details associated with the history"
    )