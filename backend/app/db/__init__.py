from .database import *
from .models import *
from .schemas import *
from .crud import *

# Tạo bảng trong database nếu chưa có
Base.metadata.create_all(bind=engine)
