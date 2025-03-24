import hashlib
from werkzeug.security import generate_password_hash
from db import models
import db as db

class AuthService:

    # Hàm đăng ký
    @staticmethod
    def register(username, password):
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = models.User(username=username, password_hash=hashed_password)
        session = db.SessionLocal()
        try:
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
        finally:
            session.close()
        return new_user