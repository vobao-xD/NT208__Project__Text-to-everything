
from PIL import Image
import cv2
import numpy as np

def preprocess_image(pil_image: Image.Image) -> Image.Image:
    # Chuyển PIL image thành OpenCV format
    img = np.array(pil_image.convert('RGB'))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Làm mịn và nhị phân hóa
    img = cv2.GaussianBlur(img, (3, 3), 0)
    img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Chuyển lại sang PIL để dùng với pytesseract
    return Image.fromarray(img)