from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything API"}

# @router.get("/docs")
# def do_nothing():
#     return {"message": "What r u doing bro???"}
