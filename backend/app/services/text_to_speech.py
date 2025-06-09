import os
from typing import Optional
from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile
import httpx
from db.schemas import TTSRequest, TTSResponse
from services.authentication_and_authorization import create_microservice_token
from services.output_manager import OutputManager
from sqlalchemy.orm import Session

load_dotenv()

class TextToSpeechService:
    # Khởi tạo API Key
    TTS_BACKEND_URL = os.getenv("TTS_BACKEND_URL")
    
    @staticmethod
    async def text_to_speech_with_default_voice(
        TTS_request: TTSRequest,    
        user_data: dict,
        db: Session
    ) -> TTSResponse:
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                tts_token = create_microservice_token("text-to-speech-default", user_data["email"])

                # Gọi endpoint /tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.TTS_BACKEND_URL}/tts",
                    headers={
                        "Authorization": f"Bearer {tts_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": TTS_request.text,
                        "language": TTS_request.language,
                        "gender": TTS_request.gender,
                        "style": TTS_request.style
                    }
                )

                response.raise_for_status()
                tts_response = response.json()

                if not tts_response.get("success"):
                    raise HTTPException(status_code=500, detail="viXTTS generation failed")

                wav_path = tts_response["file_path"]
                
                # Tải file wav từ /audio
                wav_response = await client.get(
                    f"{TextToSpeechService.TTS_BACKEND_URL}/audio/{wav_path}",
                    headers={"Authorization": f"Bearer {tts_token}"}
                )
                wav_response.raise_for_status()
                
                save_path = OutputManager.save_output_file(
                    user_email=user_data["email"],
                    generator_name="text-to-speech-default",
                    file_content=wav_response.content,
                    file_extension="wav"
                )

                OutputManager.log_chat(
                    db=db,
                    user_email=user_data["email"],
                    generator_name="text-to-speech-default",
                    input_type="text",
                    text_prompt=TTS_request.text,
                    output_type="audio",
                    output_file_path=str(save_path)
                )

                return TTSResponse(
                    success=True,
                    file_path=str(save_path),
                    timestamp=tts_response.get("timestamp", "")
                )
                
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Request to viXTTS timed out after 10 minutes")
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

    @staticmethod
    async def text_to_speech_with_custom_voice(
        db: Session,
        user_data: dict,
        text: str,
        language: str,
        use_existing_reference: bool,
        file: Optional[UploadFile],
    ) -> TTSResponse:
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                tts_token = create_microservice_token("text-to-speech-custom", user_data["email"])

                if file and not use_existing_reference:
                    file_content = await file.read()
                    files = {
                        "file": (file.filename, file_content, file.content_type)
                    }
                else:
                    files = None

                # Gọi endpoint /custom-tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.TTS_BACKEND_URL}/custom-tts",
                    headers={
                        "Authorization": f"Bearer {tts_token}"
                    },
                    data={
                        "text": text,
                        "language": language,
                        "use_existing_reference": str(use_existing_reference).lower()
                    },
                    files=files
                )

                response.raise_for_status()
                tts_response = response.json()

                if not tts_response.get("success"):
                    raise HTTPException(status_code=500, detail="viXTTS generation failed")

                wav_path = tts_response["file_path"]
                
                # Tải file wav từ /audio
                wav_response = await client.get(
                    f"{TextToSpeechService.TTS_BACKEND_URL}/audio/{wav_path}",
                    headers={"Authorization": f"Bearer {tts_token}"}
                )
                wav_response.raise_for_status()
                
                save_path = OutputManager.save_output_file(
                    user_email=user_data["email"],
                    generator_name="text-to-speech-default",
                    file_content=wav_response.content,
                    file_extension="wav"
                )

                OutputManager.log_chat(
                    db=db,
                    user_email=user_data["email"],
                    generator_name="text-to-speech-default",
                    input_type="text",
                    text_prompt=text,
                    output_type="audio",
                    output_file_path=str(save_path)
                )

                return TTSResponse(
                    success=True,
                    file_path=str(save_path),
                    timestamp=tts_response.get("timestamp", "")
                )
                
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Request to viXTTS timed out after 10 minutes")
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
