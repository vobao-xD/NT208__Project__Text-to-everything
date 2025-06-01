import os
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from db.models import ChatDetail, ChatHistory
from db import get_db

class OutputManager:
    OUTPUT_DIR = "./_output"  # Sử dụng đường dẫn tuyệt đối

    @staticmethod
    def save_output(
        user_email: str,
        chat_history_id: str,
        generator_id: str,
        input_type: str,
        text_prompt: str = None,
        input_file_path: str = None,
        output_type: str = "text",
        file_data: bytes = None,
        content: str = None,
        db: Session = Depends(get_db)
    ):
        """
        Lưu output vào hệ thống và cập nhật ChatDetail.
        - user_email: Email của user.
        - chat_history_id: ID của phiên chat.
        - generator_id: ID của generator.
        - input_type: Loại input (text, file).
        - text_prompt: Nội dung text input.
        - input_file_path: Đường dẫn file input.
        - output_type: Loại output (audio, image, video, text).
        - file_data: Dữ liệu file output (audio, image, video).
        - content: Nội dung text output.
        """
        if not db:
            raise ValueError("Database session is required")

        # Kiểm tra hoặc tạo ChatHistory
        chat_history = db.query(ChatHistory).filter(ChatHistory.id == chat_history_id).first()
        if not chat_history or str(chat_history.user_email) != user_email:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập hoặc phiên chat không tồn tại")

        # Tạo thư mục cho user
        user_dir = f"{OutputManager.OUTPUT_DIR}/{user_email}"
        os.makedirs(user_dir, exist_ok=True)

        # Xử lý file output (audio, image, video)
        file_path = None
        if file_data and output_type in ["audio", "image", "video"]:
            extension = "wav" if output_type == "audio" else "jpg" if output_type == "image" else "mp4"
            timestamp = datetime.now().isoformat().replace(":", "-")  # Tránh ký tự : trong tên file
            filename = f"{output_type}_{timestamp}.{extension}"
            file_path = f"{user_dir}/{filename}"

            try:
                with open(file_path, "wb") as f:
                    f.write(file_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Không thể lưu file: {str(e)}")

        # Tạo hoặc cập nhật ChatDetail
        chat_detail = ChatDetail(
            chat_history_id=chat_history_id,
            generator_id=generator_id,
            input_type=input_type,
            text_prompt=text_prompt,
            input_file_path=input_file_path,
            output_type=output_type,
            output_content=content if output_type == "text" else None,
            output_file_path=file_path if file_data else None,
            created_at=datetime.now()
        )
        db.add(chat_detail)
        db.commit()
        db.refresh(chat_detail)

        return {
            "id": chat_detail.id,
            "chat_history_id": chat_history_id,
            "file_path": file_path,
            "content": content,
            "type": output_type,
            "created_at": chat_detail.created_at
        }

    @staticmethod
    def get_output(user_email: str, chat_detail_id: str, db: Session = Depends(get_db)):
        """
        Truy xuất output từ ChatDetail và kiểm tra quyền.
        """
        chat_detail = db.query(ChatDetail).join(ChatHistory).filter(
            ChatDetail.id == chat_detail_id,
            ChatHistory.user_email == user_email
        ).first()

        if not chat_detail:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập hoặc output không tồn tại")

        return {
            "id": chat_detail.id,
            "chat_history_id": chat_detail.chat_history_id,
            "type": chat_detail.output_type,
            "content": chat_detail.output_content,
            "file_path": chat_detail.output_file_path,
            "created_at": chat_detail.created_at
        }

    @staticmethod
    def get_user_all_outputs(db: Session, user_email: str):
        """
        Lấy danh sách tất cả output của user qua ChatDetail.
        """
        chat_details = db.query(ChatDetail).join(ChatHistory).filter(
            ChatHistory.user_email == user_email
        ).all()
        return [
            {
                "id": detail.id,
                "chat_history_id": detail.chat_history_id,
                "type": detail.output_type,
                "content": detail.output_content,
                "file_path": detail.output_file_path,
                "created_at": detail.created_at
            }
            for detail in chat_details
        ]