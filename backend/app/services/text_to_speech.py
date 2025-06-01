import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request
import httpx
from db.schemas import UserBase, TTSRequest, TTSResponse, TTSUploadRequest
from services.authentication_and_authorization import create_microservice_token
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path
from db.models import User
from uuid import UUID
from db import get_db

import jwt

load_dotenv()

class TextToSpeechService:
    # Khởi tạo API Key
    BASEURL = os.getenv("TTS_BACKEND_URL")
    
    @staticmethod
    async def text_to_speech_with_default_voice(
        TTS_request: TTSRequest,    
        user_data: dict,
        db: Session
    ) -> TTSResponse:
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                tts_token = create_microservice_token("text-to-speech", user_data["email"])

                # Gọi endpoint /tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.BASEURL}/tts",
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

                mp3_path = tts_response["file_path"]
                
                # Tải file MP3 từ /audio
                mp3_response = await client.get(
                    f"{TextToSpeechService.BASEURL}/audio/{mp3_path}",
                    headers={"Authorization": f"Bearer {tts_token}"}
                )
                mp3_response.raise_for_status()
                
                # Tạo thư mục lưu trữ nếu chưa tồn tại
                output_dir = Path("_audio_output")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Lưu file MP3
                mp3_filename = mp3_path.split("/")[-1]
                save_path = output_dir / mp3_filename
                with open(save_path, "wb") as f:
                    f.write(mp3_response.content)

                # # Lưu lịch sử vào database
                # new_chat = ChatHistoryBase(user_id=current_user.id)
                
                # new_detail = ChatDetailBase(
                #     chat_history_id=new_chat.id,
                #     generator_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                #     input_type="text",
                #     text_prompt=f"{request.text} (language: {request.language}, gender: {request.gender}, style: {request.style})",
                #     output_type="audio",
                #     output_file_path=str(save_path)
                # )
                # db.add(new_chat)
                # db.add(new_detail)
                # db.commit()
                
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
        TTS_request: TTSUploadRequest,    
        user_data: dict,
        db: Session
    ) -> TTSResponse:
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                tts_token = create_microservice_token("text-to-speech", user_data["email"])

                validated_file = TTS_request.file
                
                if file and not use_existing_reference:
                files = {"file": open(file, "rb")}
                # Gọi endpoint /custom-tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.BASEURL}/custom-tts",
                    headers={
                        "Authorization": f"Bearer {tts_token}",
                        "Content-Type": "application/json"
                    },
                    data={
                        "text": TTS_request.text,
                        "language": TTS_request.language,
                        "use_existing_reference": str(TTS_request.use_existing_reference).lower()
                    },
                    files=files
                )

                response.raise_for_status()
                tts_response = response.json()

                if not tts_response.get("success"):
                    raise HTTPException(status_code=500, detail="viXTTS generation failed")

                mp3_path = tts_response["file_path"]
                
                # Tải file MP3 từ /audio
                mp3_response = await client.get(
                    f"{TextToSpeechService.BASEURL}/audio/{mp3_path}",
                    headers={"Authorization": f"Bearer {tts_token}"}
                )
                mp3_response.raise_for_status()
                
                # Tạo thư mục lưu trữ nếu chưa tồn tại
                output_dir = Path("_audio_output")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Lưu file MP3
                mp3_filename = mp3_path.split("/")[-1]
                save_path = output_dir / mp3_filename
                with open(save_path, "wb") as f:
                    f.write(mp3_response.content)

                # # Lưu lịch sử vào database
                # new_chat = ChatHistoryBase(user_id=current_user.id)
                
                # new_detail = ChatDetailBase(
                #     chat_history_id=new_chat.id,
                #     generator_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                #     input_type="text",
                #     text_prompt=f"{request.text} (language: {request.language}, gender: {request.gender}, style: {request.style})",
                #     output_type="audio",
                #     output_file_path=str(save_path)
                # )
                # db.add(new_chat)
                # db.add(new_detail)
                # db.commit()
                
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
    }