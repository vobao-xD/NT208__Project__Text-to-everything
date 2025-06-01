import os
from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Outputs  

class FileManager:
    OUTPUT_DIR = "/var/app-outputs"

    @staticmethod
    def save_output(db: Session, user_email: str, type: str, file_data: bytes = None, content: str = None):
        """
        Lưu output vào hệ thống.
        - file_data: Dữ liệu file (audio, image, video).
        - content: Dữ liệu text.
        - type: Loại output (audio, image, video, text).
        """
        # Tạo thư mục cho user
        user_dir = f"{FileManager.OUTPUT_DIR}/{user_email}"
        os.makedirs(user_dir, exist_ok=True)

        # Xử lý file (audio, image, video)
        file_path = None
        if file_data and type in ["audio", "image", "video"]:
            # Tạo tên file: <type>_<timestamp>.<extension>
            extension = "mp3" if type == "audio" else "jpg" if type == "image" else "mp4"
            filename = f"{type}_{datetime.now().isoformat()}.{extension}"
            file_path = f"{user_dir}/{filename}"

            # Lưu file
            with open(file_path, "wb") as f:
                f.write(file_data)

        # Lưu text hoặc metadata vào database
        output = Outputs(
            user_email=user_email,
            type=type,
            content=content if type == "text" else None,
            file_path=file_path if file_data else None
        )
        db.add(output)
        db.commit()
        db.refresh(output)

        return {
            "id": output.id,
            "file_path": file_path,
            "content": content,
            "type": type
        }

    @staticmethod
    def get_output(db: Session, user_email: str, output_id: int):
        """
        Truy xuất output từ database và kiểm tra quyền.
        """
        output = db.query(Outputs).filter(
            Outputs.id == output_id,
            Outputs.user_email == user_email
        ).first()

        if not output:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập hoặc output không tồn tại")

        return {
            "id": output.id,
            "type": output.type,
            "content": output.content,
            "file_path": output.file_path
        }

    @staticmethod
    def get_user_outputs(db: Session, user_email: str):
        """
        Lấy danh sách tất cả output của user.
        """
        outputs = db.query(Outputs).filter(Outputs.user_email == user_email).all()
        return [
            {
                "id": output.id,
                "type": output.type,
                "content": output.content,
                "file_path": output.file_path,
                "created_at": output.created_at
            }
            for output in outputs
        ]