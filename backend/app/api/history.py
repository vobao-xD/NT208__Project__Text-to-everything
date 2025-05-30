from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session,joinedload
from db.database import get_db
from db.models import ChatHistory, ChatDetail, Generator
from db.schemas import ChatCreate, ChatHistoryResponse
from services.auth import Auth

router = APIRouter()

@router.post("/chat-history", response_model=ChatHistoryResponse)
def save_chat(
    chat: ChatCreate,
    db: Session = Depends(get_db),
    current_user = Depends(Auth.get_current_user)
):

    new_chat = ChatHistory(user_id=current_user.id)
    db.add(new_chat)
    db.flush()  # Để có ID trước khi tạo ChatDetail

    for detail in chat.details:
        #Kiểm tra generator có tồn tại hay không
        generator = db.query(Generator).get(detail.generator_id)
        if not generator:
            raise HTTPException(status_code=400, detail=f"Invalid generator_id: {detail.generator_id}")
        
        new_detail = ChatDetail(
            chat_history_id=new_chat.id,
            input_type=detail.input_type,
            text_prompt=detail.text_prompt,
            input_file_name=detail.input_file_name,
            generator_id=detail.generator_id  
        )
        db.add(new_detail)

    db.commit()
    db.refresh(new_chat)
    return new_chat

@router.get("/chat-history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user = Depends(Auth.get_current_user)
):
    chats = db.query(ChatHistory)\
        .options(joinedload(ChatHistory.details))\
        .filter(ChatHistory.user_id == current_user.id)\
        .order_by(ChatHistory.created_at.desc())\
        .all()
    return chats

@router.get("/chat-history/{history_id}", response_model=ChatHistoryResponse)
def get_chat_history_by_id(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(Auth.get_current_user)
):
    chat = db.query(ChatHistory)\
        .options(joinedload(ChatHistory.details).joinedload(ChatDetail.generator))\
        .filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id)\
        .first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found or unauthorized")

    return chat

@router.delete("/chat-history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chat_history(
    history_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(Auth.get_current_user)
):
    chat_history = db.query(ChatHistory).filter(
        ChatHistory.id == history_id,
        ChatHistory.user_id == current_user.id
    ).first()

    if not chat_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat history not found or not authorized."
        )

    db.delete(chat_history)
    db.commit()
    return None  # Trả về 204 No Content