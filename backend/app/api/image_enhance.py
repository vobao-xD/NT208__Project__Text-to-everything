from fastapi import FastAPI, Depends, File, HTTPException,APIRouter, Request, UploadFile
from PIL import Image, ImageEnhance
from fastapi.responses import StreamingResponse
from requests import Session
from db.database import get_db
from services.authentication_and_authorization import verify_user_access_token
from services.history_and_output_manager import HistoryAndOutputManager
import io

router=APIRouter()

@router.post('/enhance')
async def enhance_image(request: Request, file: UploadFile=File(...), db: Session = Depends(get_db)):
    user_data = verify_user_access_token(source="cookie", request=request)
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400,detail="File phải là hình ảnh")
    try:

        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        #1 Cải thiện độ sáng
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        #2 Điều chỉnh độ sáng
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(1.1)

        #3 Điều chỉnh độ tương phản
        enhancer = ImageEnhance.Contrast(image)
        image = enchane_image=enhancer.enhance(1.2)

        #Lưu hình ảnh
        output_buffer=io.BytesIO()
        enchane_image.save(output_buffer, format="JPEG", quality=95)
        output_buffer.seek(0)

        save_path = HistoryAndOutputManager.save_output_file(
                    user_email=user_data["email"],
                    generator_name="image-quality-enhancing",
                    file_content=output_buffer,
                    file_extension="jpeg"
                )
        
        HistoryAndOutputManager.log_chat(
                    db=db,
                    user_email=user_data["email"],
                    generator_name="image-quality-enhancing",
                    input_type="",
                    text_prompt="improve this image quality",
                    output_type="audio",
                    output_file_path=str(save_path)
                )
        

        #Trả về hình ảnh
        return StreamingResponse(
            output_buffer,
            media_type="image/JPEG",
            headers={"Content-Disposition": f"attachment; filename=enhanced_image.jpg"}
        )

    except Exception as ex:
        raise HTTPException(status_code=400,detail=f"Lỗi khi xử lí hình ảnh")
