from fastapi import APIRouter
from . import authentication, chat_history, chatbot_content, check_api, image_enhance, payment_with_momo, text_to_speech, text_to_image, text_to_video, general, input,generate_answer, text_to_code, role, advanced_model

router = APIRouter()

router.include_router(general.router, prefix="", tags=["General"])
router.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
router.include_router(text_to_speech.router, prefix="/text-to-speech", tags=["Text to speech"])
router.include_router(text_to_image.router, prefix="/text-to-image", tags=["Text to image"])
router.include_router(text_to_video.router, prefix="/text-to-video", tags=["Text to video"])
router.include_router(text_to_code.router,prefix="/text-to-code",tags=["Text to code"])
router.include_router(chat_history.router, prefix="", tags=["Chat history"])
router.include_router(payment_with_momo.router,prefix="",tags=["Payment"])
router.include_router(input.router,prefix="",tags=["Input proccessing"])
router.include_router(chatbot_content.router,prefix="",tags=["Content generative chatbot"])
router.include_router(image_enhance.router,prefix="",tags=["Image enhancing"])
router.include_router(check_api.router,prefix="",tags=["Check permission"])
router.include_router(generate_answer.router,prefix="",tags=["Generate answer"])
router.include_router(role.router,prefix="",tags=["Role"])
router.include_router(advanced_model.router,prefix="",tags=["Advanced model"])