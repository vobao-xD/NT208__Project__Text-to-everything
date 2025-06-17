from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ChatHistory
from db.schemas import ChatCreate, ChatHistoryResponse, ChatDetailCreate, ChatDetailResponse
from services.authentication_and_authorization import *
from services.history_and_output_manager import HistoryAndOutputManager

router = APIRouter()

def validate_file_type(filename: str, expected_type: str) -> bool:
    ext = filename.split(".")[-1].lower()
    valid_extensions = {
        "audio": ["mp3", "wav"],
        "image": ["png", "jpg", "jpeg"],
        "video": ["mp4", "avi", "mov"],
        "file": ["pdf", "txt", "doc", "docx"]
    }
    return ext in valid_extensions.get(expected_type, [])

@router.post("/chat-history", response_model=ChatHistoryResponse)
def save_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return HistoryAndOutputManager.log_chat(chat, db, current_user.email)

@router.post("/chat-history/{history_id}/add-detail", response_model=ChatDetailResponse)
def add_detail_to_chat(
    history_id: str, 
    detail: ChatDetailCreate, 
    db: Session = Depends(get_db), 
    current_user=Depends(get_current_user)
):
    chat = db.query(ChatHistory).filter(ChatHistory.id == history_id, ChatHistory.user_email == current_user.email).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # if detail.input_file_name and not validate_file_type(detail.input_file_name, detail.input_type):
    #     raise HTTPException(status_code=400, detail=f"Định dạng file không phù hợp với {detail.input_type}")
    # if detail.output_file_name and not validate_file_type(detail.output_file_name, detail.output_type):
    #     raise HTTPException(status_code=400, detail=f"Định dạng file không phù hợp với {detail.output_type}")
    return HistoryAndOutputManager.add_chat_detail(
        db,
        chat_history_id=history_id,
        input_type=detail.input_type,
        input_text=detail.input_text,
        input_file_name=detail.input_file_name,
        input_file_path=detail.input_file_path,
        output_type=detail.output_type,
        output_text=detail.output_text,
        output_file_path=detail.output_file_path,
        output_file_name=detail.output_file_name,
        generator_id=detail.generator_id
    )

@router.get("/chat-history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    limit: int = 10
):
    return HistoryAndOutputManager.get_user_chat_histories(db, current_user.email, limit=limit)

@router.get("/chat-history/{history_id}", response_model=ChatHistoryResponse)
def get_chat_history_by_id(
    history_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return HistoryAndOutputManager.get_chat_history_by_id(db, history_id, current_user.email)

@router.delete("/chat-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_history(
    history_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return HistoryAndOutputManager.delete_chat_history(history_id, db, current_user.email)
