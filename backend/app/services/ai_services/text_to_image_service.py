import requests
import asyncio
import base64
import json
import os
from dotenv import load_dotenv
from googletrans import Translator
from db.schemas import TTIPrompt
import secrets

load_dotenv()

class TextToImageService:
    """
    Chuyển văn bản thành hình ảnh, dịch văn bản qua tiếng Anh và yêu cầu API của Cloudflare để tạo.\n
    **Known issue(s)**: Với hàm `getImageSlow()`, có khả năng model `stabilityai/stable-diffusion-xl-base-1.0` sẽ trả về hình rỗng, lúc đó khuyến khích người dùng chuyển model hoặc chờ trong vòng 10-20s\n
    """
    # Khởi tạo API Key, Acount,...
    head = {
        "Authorization": f"Bearer {os.getenv('TTI_API_KEY')}"
    }
    accountId = os.getenv("TTI_ACCOUNT_ID")

    # Hàm hỗ trợ dịch tiếng Việt sang tiếng Anh để cho kết quả từ API chính xác hơn
    @staticmethod 
    async def translateText(text: str):
        """
        Dịch ngôn ngữ một cách tự động bằng API của Google Translate, trả về kiểu dữ liệu Translated\n
        :param text: văn bản cần dịch\n
        :return: văn bản đã được dịch\n
        >>> translateText("Xin chào!").text
        'Hello!'
        """
        async with Translator() as translator:
            result = await translator.translate(text)
            return result
        


    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def getImage(prompt: str | None, steps: int = 4):
        """
        .. |language| replace:: Python
        Gửi yêu cầu chuyển đổi văn bản thành hình ảnh bằng API của Cloudflare\n
        Tuy nhiên, việc chuyển từ các tiếng khác sang tiếng Anh sẽ có thế khiến cho bản tiếng Anh trở nên dài hơn 2048 ký tự, thông báo người dùng nếu chuyện này xảy ra.\n
        :param prompt: Văn bản cần chuyển thành hình ảnh (bắt buộc), giới hạn tối đa 2048 ký tự\n
        :param num_steps: Số bước cần để tạo ảnh, mặc định là 4, tối đa là 8. Càng cao càng chính xác nhưng sẽ tạo lâu hơn\n
        :return: Ảnh được định dạng bằng Base64\n
        >>> getImage("cyberpunk cat")
        [some Base64 strings...]
        """
        if prompt is None:
            return 'Error 404: No prompt'
        elif len(prompt) > 2048:
            return 'Error 404: Prompt too long'
        url = f'https://api.cloudflare.com/client/v4/accounts/{TextToImageService.accountId}/ai/run/@cf/black-forest-labs/flux-1-schnell'
        body = json.dumps(
                {
                    'prompt':prompt,
                    'steps':steps
                }
            )
        response = requests.post(url, body, headers=TextToImageService.head)
        successCode = response.status_code
        if successCode == 200:
            image = json.loads(response.text)['result']['image']
            image_bytes = base64.b64decode(image)
            file_name = "./img/" + base64.b64encode(secrets.token_bytes(12), b"-_").decode() + ".png"
            with open(file_name, "wb") as f:
                f.write(image_bytes)
            return file_name.removeprefix('./')
        else:
            return f"Error {response.status_code}: {response.text}"
        

    
    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def textToImage(prompt: TTIPrompt):
        '''
        prompt: str
        steps: int | None = None
        '''
        enPrompt = asyncio.run(TextToImageService.translateText(prompt.prompt)).text
        image = TextToImageService.getImage(enPrompt, prompt.steps)
        return image