import os
import requests
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from sqlalchemy.orm import Session
from db.schemas import TTVResponse
from services.output_manager import OutputManager

load_dotenv()

class TextToVideoService:
    TTV_MODEL_URL =  os.getenv("TTV_MODEL_URL")
    TTV_API_KEYS = os.getenv("TTV_API_KEYS", "").split(",")

    @staticmethod 
    def translateText(text: str) -> str:
        """
        Dịch ngôn ngữ một cách tự động bằng API của Google Translate, trả về kiểu dữ liệu Translated\n
        :param text: văn bản cần dịch\n
        :return: văn bản đã được dịch\n
        >>> translateText("Xin chào!").text
        'Hello!'
        """
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated
        
    @staticmethod
    def textToVideo(db: Session, user_data: dict, payload: dict) -> bytes:
        last_error = None

        for key in TextToVideoService.TTV_API_KEYS:
            key = key.strip()
            headers = {"x-api-key": key}

            response = requests.post(
                TextToVideoService.TTV_MODEL_URL,
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                print(f"✅ Thành công với key: {key}")
                
                save_path = OutputManager.save_output_file(
                    user_email=user_data["email"],
                    generator_name="text-to-video",
                    file_content=response.content,
                    file_extension="mp4"
                )

                OutputManager.log_chat(
                    db=db,
                    user_email=user_data["email"],
                    generator_name="text-to-video",
                    input_type="text",
                    text_prompt=str(payload),
                    output_type="video",
                    output_file_path=str(save_path)
                )

                return TTVResponse(
                    success=True,
                    file_path=str(save_path),
                )

            # Nếu API Key hết credit 
            if (response.status_code == 406 or 
                "insufficient credits" in response.text.lower()):
                print(f"⚠️ API key {key} đã hết credit. Thử key tiếp theo...")
                last_error = f"{response.status_code} - {response.text}"
                continue

            # Nếu lỗi khác, dừng lại
            raise Exception(f"API error: {response.status_code} - {response.text}")

        raise Exception(f"Tất cả API key đều thất bại. Lỗi cuối: {last_error}")