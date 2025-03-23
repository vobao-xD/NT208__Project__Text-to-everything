from fastapi import FastAPI
from api import router
from db import init_db

# app = FastAPI(docs_url=None, redoc_url=None) -> Disable docs and redoc
app = FastAPI()

# Khởi tạo database nếu chưa có
init_db()

# Lấy các route để xử lý truy vấn
app.include_router(router)

# Main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
