from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
from db.models import Generator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup SQLAlchemy
engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False, autoflush=False)
Base = declarative_base()
session = SessionLocal()

# Danh sách generator cần chèn
generators_to_insert = [
    {"name": "text-to-speech-default", "input_type": "text", "output_type": "audio"},
    {"name": "text-to-speech-custom", "input_type": "text", "output_type": "audio"},
    {"name": "text-to-image", "input_type": "text", "output_type": "image"},
    {"name": "text-to-video", "input_type": "text", "output_type": "video"},
]

try:
    for gen in generators_to_insert:
        exists = session.query(Generator).filter_by(name=gen["name"]).first()
        if not exists:
            session.add(Generator(**gen))
    session.commit()
except IntegrityError:
    session.rollback()
    print("Dữ liệu đã tồn tại, rollback.")
finally:
    session.close()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
