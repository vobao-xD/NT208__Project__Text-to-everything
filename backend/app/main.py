from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
from db import init_db, get_db

# app = FastAPI(docs_url=None, redoc_url=None) -> Disable docs and redoc (tạm chưa dùng)
app = FastAPI()

# Cấu hình CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo database nếu chưa có
init_db()

# Lấy các route để xử lý truy vấn
app.include_router(router)

# Main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
