import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
import httpx
from db.schemas import UserBase, TTSRequest, TTSResponse, ChatHistoryBase
from services.authentication_and_authorization import Auth
from sqlalchemy.orm import Session
from db import get_db

load_dotenv()

class TextToSpeechService:
    # Khởi tạo API Key
    BASEURL = os.getenv("TTS_BACKEND_URL")
    
    @staticmethod
    async def text_to_speech_with_default_voice(
        request: TTSRequest,
        current_user: dict,
        db: Session
    ) -> TTSResponse:
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                # Tạo access token cho user
                access_token = Auth.create_access_token(data={"sub": current_user.email})
                
                # Gọi endpoint /tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.BASEURL}/tts",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": request.text,
                        "language": request.language,
                        "gender": request.gender,
                        "style": request.style
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
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                mp3_response.raise_for_status()
                
                # Lưu file MP3 tạm thời
                mp3_filename = mp3_path.split("/")[-1]
                save_path = f"../../_audio_output/{mp3_filename}"
                with open(save_path, "wb") as f:
                    f.write(mp3_response.content)

                new_chat = ChatHistory(user_id=current_user.id)
                new_detail = ChatDetail(
                    chat_history_id=new_chat.id,
                    generator_id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                    input_type="text",
                    text_prompt=f"{request.text} (language: {request.language}, gender: {request.gender}, style: {request.style})",
                    output_type="audio",
                    output_file_path=str(save_path)
                )
                db.add(new_detail)
                db.commit()
                
                return {"success": True, "mp3_file": save_path}
                
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Request to viXTTS timed out after 10 minutes")
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
