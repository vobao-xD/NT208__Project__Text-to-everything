from pathlib import Path
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import datetime
from db.models import ChatHistory, ChatDetail
import uuid

class OutputManager:

    @staticmethod
    def create_chat_history(db: Session, user_email: str) -> ChatHistory:
        history = ChatHistory(user_email=user_email)
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    @staticmethod
    def create_chat_detail(db: Session, **kwargs) -> ChatDetail:
        detail = ChatDetail(**kwargs)
        db.add(detail)
        db.commit()
        db.refresh(detail)
        return detail
    
    def get_user_chat_histories(db: Session, user_email: str, limit: int = 50):
        return db.query(ChatHistory).filter(ChatHistory.user_email == user_email)\
            .order_by(ChatHistory.created_at.desc()).limit(limit).all()

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

    @staticmethod
    def log_chat(
        db: Session,
        user_email: str,
        generator_name: str,
        input_type: str,
        text_prompt: str,
        output_type: str,
        output_content: str = None,
        output_file_path: str = None,
        input_file_path: str = None,
    ) -> UUID:
        history = OutputManager.create_chat_history(db, user_email=user_email)
        detail = OutputManager.create_chat_detail(
            db=db,
            chat_history_id=history.id,
            generator_name=generator_name,
            input_type=input_type,
            text_prompt=text_prompt,
            input_file_path=input_file_path,
            output_type=output_type,
            output_content=output_content,
            output_file_path=output_file_path
        )
        return history.id
