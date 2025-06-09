from fastapi import APIRouter
from services import TextToImageService as service
from db import schemas

router = APIRouter()

@router.post("/")
def text_to_image(prompt: schemas.TTIPrompt) -> dict[str, str]:
    """
    Chuyển văn bản thành hình ảnh bằng AI (nhanh)
    """
    image = service.textToImage(prompt)
    # db: Session= Depends(get_db)
    # db.execute(insert())
    if image.startswith("Error "):
        return {"Error": image.removeprefix("Error ")}
    return {"image_url" : image}

    
