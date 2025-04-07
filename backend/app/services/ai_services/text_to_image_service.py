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
        
    # Tạo ảnh tốc độ chậm
    @staticmethod
    def getImageSlow(prompt: str | None, negative_prompt: str = '', height = 512, width = 512, num_steps = 20, guidance = 7.5, model=0):
        """
        .. |language| replace:: Python
        Gửi yêu cầu chuyển đổi văn bản thành hình ảnh bằng API của Cloudflare (nhiều tham số)\n
        :param prompt: Văn bản cần chuyển thành hình ảnh (bắt buộc)\n
        :param negative_prompt: Văn bản liệt kê các yếu tố để né trong quá trình tạo\n
        :param height: Chiều cao của ảnh tính bằng pixel, mặc định là 512, tối đa là 2048 (vì để 256 thì ảnh đôi lúc sẽ hỏng).\n
        :param width: Chiều rộng của ảnh tính bằng pixel, mặc định là 512, tối đa là 2048 (vì để 256 thì ảnh đôi lúc sẽ hỏng).\n
        :param num_steps: Số bước cần để tạo ảnh, mặc định và tối đa là 20. Càng cao càng chính xác nhưng sẽ tạo lâu hơn\n
        :param guidance: Mức độ theo sát văn bản, càng cao thì ảnh sẽ càng chính xác. Mặc định là 7.5\n
        :param model: Chọn loại model: stabilityai/stable-diffusion-xl-base-1.0 (0) hoặc bytedance/stable-diffusion-xl-lightning (1). Mặc định là 0\n
        :return: Ảnh được định dạng bằng Base64\n
        >>> getImageSlow("cyberpunk cat")
        [some Base64 strings...]
        """
        if prompt is None:
            return 'Error 404: No prompt'
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
                return f"Error {response.status_code}: {response.text}"
        else:
            return f"Error 404: Model not found"

    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def getImageQuick(prompt: str | None, steps: int = 4):
        """
        .. |language| replace:: Python
        Gửi yêu cầu chuyển đổi văn bản thành hình ảnh bằng API của Cloudflare (ít tham số)\n
        Tuy nhiên, việc chuyển từ các tiếng khác sang tiếng Anh sẽ có thế khiến cho bản tiếng Anh trở nên dài hơn 2048 ký tự, thông báo người dùng nếu chuyện này xảy ra.\n
        :param prompt: Văn bản cần chuyển thành hình ảnh (bắt buộc), giới hạn tối đa 2048 ký tự\n
        :param num_steps: Số bước cần để tạo ảnh, mặc định là 4, tối đa là 8. Càng cao càng chính xác nhưng sẽ tạo lâu hơn\n
        :return: Ảnh được định dạng bằng Base64\n
        >>> getImageQuick("cyberpunk cat")
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
            return image
        else:
            return f"Error {response.status_code}: {response.text}"
        
    # Tạo ảnh tốc độ chậm 
    @staticmethod
    def textToImageSlow(prompt: SlowPrompt):
        '''
        prompt: str\n
        negative_prompt: str | None = None\n
        height: int | None = None\n
        width: int | None = None\n
        num_steps: int | None = None\n
        guidance: float | None = None\n
        model: int | None = None\n
        '''
        enPrompt = asyncio.run(TextToImageService.translateText(str(prompt.prompt))).text
        image = TextToImageService.getImageSlow(enPrompt, prompt.negative_prompt, prompt.height, prompt.width, prompt.num_steps, prompt.guidance, prompt.model)
        return image
    
    # Tạo ảnh tốc độ nhanh
    @staticmethod
    def textToImageQuick(prompt: QuickPrompt):
        '''
        prompt: str
        steps: int | None = None
        '''
        enPrompt = asyncio.run(TextToImageService.translateText(prompt.prompt)).text
        image = TextToImageService.getImageQuick(enPrompt, prompt.steps)
        return image