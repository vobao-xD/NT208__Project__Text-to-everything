import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TextToSpeechService:

    # Khởi tạo API Key
    url = 'https://api.fpt.ai/hmi/tts/v5'
    api_key = os.getenv('TTS_API_KEY')

    # Chuyển văn bản thành giọng nói
    @staticmethod
    def text_to_speech(text, voice='banmai', speed=''):
        """
        Gửi yêu cầu chuyển đổi văn bản thành giọng nói bằng API FPT.AI\n
        :param text: Văn bản cần chuyển thành giọng nói\n
        :param voice: Giọng nói sử dụng\n 
        * banmai : nữ miền Bắc\n
        * leminh : nam miền Bắc\n
        * thuminh : nữ miền Bắc\n
        * minhquang : nam miền Bắc\n
        * myan : nữ miền Trung\n
        * linhsan : nữ miền Nam\n
        * giahuy : nam miền Trung\n
        * lannhi : nữ miền Nam\n
        * ngoclam : nữ miền Trung\n
        :param speed: Tốc độ đọc (-3 đến 3, mặc định là 0)\n
        :return: URL file âm thanh hoặc thông tin lỗi\n
        """

        if not TextToSpeechService.api_key:
            raise ValueError("API key is missing. Please set TTS_API_KEY in .env file")

        headers = {
            'api-key': TextToSpeechService.api_key,
            'speed': str(speed),
            'voice': voice
        }

        response = requests.post(TextToSpeechService.url, data=text.encode('utf-8'), headers=headers)
        if response.status_code == 200:
            return response.json().get('async', "No URL returned")
        else:
            return f"Error {response.status_code}: {response.text}"
        
