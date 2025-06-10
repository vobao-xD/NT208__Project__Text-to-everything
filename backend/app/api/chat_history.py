from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ChatHistory
from db.schemas import ChatCreate, ChatHistoryResponse, ChatDetailCreate, ChatDetailResponse
from services.authentication_and_authorization import *
from services.history_and_output_manager import HistoryAndOutputManager

router = APIRouter()

@router.post("/chat-history", response_model=ChatHistoryResponse)
def save_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return HistoryAndOutputManager.log_chat(chat, db, current_user.user_email)

@router.post("/chat-history/{history_id}/add-detail", response_model=ChatDetailResponse)
def add_detail_to_chat(
    history_id: str, 
    detail: ChatDetailCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    chat = db.query(ChatHistory).filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    return HistoryAndOutputManager.add_chat_detail(
        chat_history_id = history_id,

        input_type=detail.input_type,
        input_text=detail.input_text,
        input_file_path=detail.input_file_path,

        output_type=detail.output_type,
        output_text=detail.output_text,
        output_file_path=detail.output_file_path,

        generator_id=detail.generator_id,
    )

@router.get("/chat-history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return HistoryAndOutputManager.get_user_chat_histories(db, current_user.email)

@router.get("/chat-history/{history_id}", response_model=ChatHistoryResponse)
def get_chat_history_by_id(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return HistoryAndOutputManager.get_chat_history_by_id(db, history_id, current_user.user_email)

@router.delete("/chat-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_history(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return HistoryAndOutputManager.delete_chat_history(history_id, db, current_user.user_email)

