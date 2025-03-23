from pydantic import BaseModel

class SlowPrompt(BaseModel):
    prompt: str
    negative_prompt: str
    height: int
    width: int
    num_steps: int
    guidance: float
    model: int

class QuickPrompt(BaseModel):
    prompt: str
    steps: int

