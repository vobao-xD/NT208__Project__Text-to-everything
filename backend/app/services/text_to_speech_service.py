import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
import httpx
from db.schemas import UserBase, TTSRequest
from backend.app.services.auth_service import Auth
from sqlalchemy.orm import Session
from db import get_db
from core.security import create_access_token

load_dotenv()

class TextToSpeechService:

    # Khởi tạo API Key
    url = os.getenv("TTS_BACKEND_URL")

    @staticmethod
    async def text_to_speech_with_default_voice(
        request: TTSRequest,
        current_user: UserBase = Depends(Auth.get_current_user),
        db: Session = Depends(get_db)
    ):
        async with httpx.AsyncClient(timeout=600.0) as client:
            try:
                # Tạo access token cho user
                access_token = create_access_token(data={"sub": current_user.email})
                
                # Gọi endpoint /tts của viXTTS
                response = await client.post(
                    f"{TextToSpeechService.url}/tts",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": prompt,
                        "language": language,
                        "gender": gender,
                        "style": style
                    }
                )
                response.raise_for_status()
                tts_response = response.json()
                mp3_path = tts_response["file_path"]
                
                # Tải file MP3 từ /audio
                mp3_response = await client.get(
                    f"{TextToSpeechService.url}/audio/{mp3_path}",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                mp3_response.raise_for_status()
                
                # Lưu file MP3 tạm thời
                mp3_filename = mp3_path.split("/")[-1]
                save_path = f"../../_audio_output/{mp3_filename}"
                with open(save_path, "wb") as f:
                    f.write(mp3_response.content)
                
                return {"success": True, "mp3_file": save_path}
                
            except httpx.HTTPStatusError as e:
                raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Request to viXTTS timed out after 10 minutes")
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")


        
