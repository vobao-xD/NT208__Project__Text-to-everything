
import contextlib
import os

from fastapi import FastAPI
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

openai_client_instance: AsyncOpenAI | None = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing OpenAI client...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
    client = AsyncOpenAI(api_key=api_key)
    app.state.openai_client_instance = client
    yield
    print("Application shutdown: Closing OpenAI client...")
    await client.close()