from fastapi import APIRouter
from . import auth, text_to_speech, text_to_image, text_to_video, general, history,MOMO,input,ChatBotContent,enhance,Check_api,generate_answer,text_to_code,role,advanced_model

router = APIRouter()

router.include_router(general.router, prefix="", tags=["General"])
router.include_router(auth.router, prefix="", tags=["Auth"])
router.include_router(text_to_speech.router, prefix="/text-to-speech", tags=["Text-to-Speech"])
router.include_router(text_to_image.router, prefix="/text-to-image", tags=["Text-to-Image"])
router.include_router(text_to_video.router, prefix="/text-to-video", tags=["Text-to-Video"])
router.include_router(text_to_code.router,prefix="/text-to-code",tags=["Text to Code"])
router.include_router(history.router, prefix="", tags=["History"])
# router.include_router(login.router,prefix="",tags=["login"])
router.include_router(MOMO.router,prefix="",tags=["Payment"])
router.include_router(input.router,prefix="",tags=["Xử lý input"])
router.include_router(ChatBotContent.router,prefix="",tags=["ChatBot Content"])
router.include_router(enhance.router,prefix="",tags=["Enhance"])
router.include_router(Check_api.router,prefix="",tags=["Check Permission"])
router.include_router(generate_answer.router,prefix="",tags=["Generate Answer"])
router.include_router(role.router,prefix="",tags=["Role"])
router.include_router(advanced_model.router,prefix="",tags=["Advanced Model"])
