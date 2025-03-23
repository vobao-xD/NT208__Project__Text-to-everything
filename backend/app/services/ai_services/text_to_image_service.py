import requests
import asyncio
import base64
import json
import os
from dotenv import load_dotenv
from googletrans import Translator
from db.schemas import SlowPrompt, QuickPrompt

load_dotenv()

class TextToImageService:

    # Khởi tạo API Key, Acount,...
    head = {
        "Authorization": f"Bearer {os.getenv('TTI_API_KEY')}"
    }
    accountId = os.getenv("TTI_ACCOUNT_ID")

    # Hàm hỗ trợ dịch tiếng Việt sang tiếng Anh để cho kết quả từ API chính xác hơn
    @staticmethod 
    async def translateText(text: str):
        async with Translator() as translator:
            result = await translator.translate(text)
            return result
        
    # Tạo ảnh tốc độ chậm
    @staticmethod
    def getImageSlow(prompt: str | None, negative_prompt: str = '', height = 512, width = 512, num_steps = 20, guidance = 7.5, model=0):
        if prompt is None:
            return 'No prompt'
        sub_url = ['stabilityai/stable-diffusion-xl-base-1.0','bytedance/stable-diffusion-xl-lightning']
        url = f'https://api.cloudflare.com/client/v4/accounts/{TextToImageService.accountId}/ai/run/@cf/{sub_url[model]}'
        if model in [0,1]:
            body = json.dumps(
                {
                    'prompt':prompt,
                    'negative_prompt':negative_prompt,
                    'height':height,
                    'width':width,
                    'num_steps':num_steps,
                    'guidance':guidance
                }
            )
            response = requests.post(url, body, headers=TextToImageService.head)
            successCode = response.status_code
            if successCode == 200:
                image = response.content
                return base64.b64encode(image)
            else:
                return 'Something went wrong'

    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def getImageQuick(prompt: str | None, steps: int = 4):
        if prompt is None:
            return 'No prompt'
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
            return image
        else:
            return 'Something went wrong'
        
    # Tạo ảnh tốc độ chậm 
    @staticmethod
    def textToImageSlow(prompt: SlowPrompt):
        enPrompt = asyncio.run(TextToImageService.translateText(str(prompt.prompt))).text
        image = TextToImageService.getImageSlow(enPrompt, prompt.negative_prompt, prompt.height, prompt.width, prompt.num_steps, prompt.guidance, prompt.model)
        return image
    
    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def textToImageQuick(prompt: QuickPrompt):
        enPrompt = asyncio.run(TextToImageService.translateText(prompt.prompt)).text
        image = TextToImageService.getImageQuick(enPrompt, prompt.steps)
        return image