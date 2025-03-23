import requests
import asyncio
import base64
import json
import os
from dotenv import load_dotenv
from googletrans import Translator
from db.schemas import *

load_dotenv()

class TextToImageService:

    # Khởi tạo API Key, Acount,...
    def __init__(self):
        self.head = {
            "Authorization": f"Bearer {os.getenv('TTI_API_KEY')}"
        }
        self.accountId = os.getenv("TTI_ACCOUNT_ID")

    # Hàm hỗ trợ dịch tiếng Việt sang tiếng Anh để cho kết quả từ API chính xác hơn
    async def translateText(self, text: str):
        async with Translator() as translator:
            result = await translator.translate(text)
            return result
        
    # Tạo ảnh chất lượng cao (nhưng chậm hơn)
    def getImageSlow(self, prompt: str | None, negative_prompt: str = '', 
                     height = 512, width = 512, num_steps = 20, guidance = 7.5, model = 0):
        
        if prompt is None:
            return 'No prompt'
        
        url = f'https://api.cloudflare.com/client/v4/accounts/{self.accountId}/ai/run/@cf/{sub_url[model]}'
        sub_url = ['stabilityai/stable-diffusion-xl-base-1.0','bytedance/stable-diffusion-xl-lightning']
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
            response = requests.post(url, body, headers=self.head)
            successCode = response.status_code
            if successCode == 200:
                image = response.content
                return base64.b64encode(image)
            else:
                return 'Something went wrong'

    # Tạo ảnh nhanh hơn
    def getImageQuick(self, prompt: str | None, steps: int = 4):
        if prompt is None:
            return 'No prompt'
        url = f'https://api.cloudflare.com/client/v4/accounts/{self.accountId}/ai/run/@cf/black-forest-labs/flux-1-schnell'
        body = json.dumps(
                {
                    'prompt':prompt,
                    'steps':steps
                }
            )
        response = requests.post(url, body, headers=self.head)
        successCode = response.status_code
        if successCode == 200:
            image = json.loads(response.text)['result']['image']
            return image
        else:
            return 'Something went wrong'
        
    # Chuyển văn bản thành hình ảnh (chậm)
    def textToImageSlow(self, prompt: SlowPrompt):
        enPrompt = asyncio.run(self.translateText(self, prompt.prompt)).text
        image = self.getImageSlow(self, enPrompt, prompt.negative_prompt, prompt.height, prompt.width, prompt.num_steps, prompt.guidance, prompt.model)
        return image
    
    # Chuyển văn bản thành hình ảnh (nhanh)
    def textToImageQuick(self, prompt: QuickPrompt):
        enPrompt = asyncio.run(self.translateText(prompt.prompt)).text
        image = self.getImageQuick(enPrompt, prompt.steps)
        return image