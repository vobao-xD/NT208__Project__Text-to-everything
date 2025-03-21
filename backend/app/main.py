from fastapi import FastAPI
from api import router

# app = FastAPI(docs_url=None, redoc_url=None)
app = FastAPI()

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Text-to-Everything API"}

@app.get("/docs")
def do_nothing():
    return {"message": "What r u doing bro???"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
