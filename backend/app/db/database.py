from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get database connection information from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models to inherit
Base = declarative_base()

# # Dependency to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
        print("Database connected") 
    except Exception as e:
        print(f"Database connection failed: {e}")
    finally:
        db.close()
