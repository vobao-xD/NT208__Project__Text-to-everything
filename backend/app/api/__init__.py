from fastapi import APIRouter
from . import auth, speech_to_text, text_to_speech, text_to_image, text_to_video, general, history, login

router = APIRouter()

router.include_router(general.router, prefix="", tags=["General"])
router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(speech_to_text.router, prefix="/speech-to-text", tags=["Speech-to-Text"])
router.include_router(text_to_speech.router, prefix="/text-to-speech", tags=["Text-to-Speech"])
router.include_router(text_to_image.router, prefix="/text-to-image", tags=["Text-to-Image"])
router.include_router(text_to_video.router, prefix="/text-to-video", tags=["Text-to-Video"])
router.include_router(history.router, prefix="/history", tags=["History"])
router.include_router(login.router,prefix="",tags=["login"])