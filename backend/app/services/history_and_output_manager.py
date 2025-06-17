import logging
from pathlib import Path
from fastapi import HTTPException
from grpc import Status
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from db.schemas import ChatCreate, ChatHistoryResponse
from db.models import ChatHistory, ChatDetail, Generator
import uuid

class HistoryAndOutputManager:

    @staticmethod
    def create_chat_history(db: Session, user_email: str) -> ChatHistory:
        history = ChatHistory(user_email=user_email)
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    @staticmethod
    def add_chat_detail(db: Session, **kwargs) -> ChatDetail:
        detail = ChatDetail(**kwargs)
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return detail
    
    @staticmethod
    def get_user_chat_histories(db: Session, user_email: str, limit: int = 10) -> list[ChatHistoryResponse]:
        return db.query(ChatHistory).filter(ChatHistory.user_email == user_email)\
            .order_by(ChatHistory.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_chat_history_by_id(db: Session, history_id: str, user_email: str) -> ChatHistoryResponse:
        chat = db.query(ChatHistory)\
            .options(joinedload(ChatHistory.chat_details).joinedload(ChatDetail.generator))\
            .filter(ChatHistory.id == history_id, ChatHistory.user_email == user_email)\
            .first()

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found or unauthorized")

        return chat

    @staticmethod
    def delete_chat_history(history_id: str, db: Session, user_email: str):
        chat_history = db.query(ChatHistory).filter(
        ChatHistory.id == history_id,
        ChatHistory.user_email == user_email
        ).first()

        if not chat_history:
            raise HTTPException(
                status_code=Status.HTTP_404_NOT_FOUND,
                detail="Chat history not found or not authorized."
            )
        db.delete(chat_history)
        db.commit()
        return None  # Trả về 204 No Content

    @staticmethod
    def log_chat(   
        chat: ChatCreate,
        db: Session,
        user_email: str,
    ) -> ChatHistoryResponse:
        new_chat = HistoryAndOutputManager.create_chat_history(db, user_email)
        for detail in chat.chat_details:
            #Kiểm tra generator có tồn tại hay không
            generator = db.query(Generator).get(detail.generator_id)
            if not generator:
                raise HTTPException(status_code=400, detail=f"Invalid generator_id: {detail.generator_id}")
            
            HistoryAndOutputManager.add_chat_detail(
                db,
                chat_history_id=new_chat.id,
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
        return new_chat

    @staticmethod
    def save_output_file(user_email: str, generator_name: str, file_content: bytes, file_extension: str) -> Path:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        output_dir = Path(f"./_outputs/{user_email}/{generator_name}/{today}")
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.{file_extension}"
        save_path = output_dir / filename

        with open(save_path, "wb") as f:
            f.write(file_content)

        return save_path
