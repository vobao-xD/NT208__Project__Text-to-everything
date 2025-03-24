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
        db.Session.add(new_user)
        db.Session.commit()
        return new_user