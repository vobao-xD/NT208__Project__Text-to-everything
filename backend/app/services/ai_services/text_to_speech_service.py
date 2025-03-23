import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TextToSpeechService:

    # Khởi tạo API Key
    def __init__(self):
        self.url = 'https://api.fpt.ai/hmi/tts/v5'
        self.api_key = os.getenv('TTS_API_KEY')

    # Chuyển văn bản thành giọng nói
    def text_to_speech(self, text, voice='banmai', speed=''):
        """
        Gửi yêu cầu chuyển đổi văn bản thành giọng nói bằng API FPT.AI
        :param text: Văn bản cần chuyển thành giọng nói
        :param voice: Giọng nói sử dụng (đọc trên trang của FTP để biết rõ hơn)
        :param speed: Tốc độ đọc (-3 đến 3, mặc định là 0)
        :return: URL file âm thanh hoặc thông tin lỗi
        """

        if not self.api_key:
            raise ValueError("API key is missing. Please set TTS_API_KEY in .env file")

        headers = {
            'api-key': self.api_key,
            'speed': str(speed),
            'voice': voice
        }

        response = requests.post(self.url, data=text.encode('utf-8'), headers=headers)
        if response.status_code == 200:
            return response.json().get('async', "No URL returned")
        else:
            return f"Error {response.status_code}: {response.text}"
        
