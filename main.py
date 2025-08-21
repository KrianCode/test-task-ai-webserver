from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from openai import OpenAI
from fastapi.responses import RedirectResponse

OPENROUTER_API_KEY = "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"
MODEL_NAME = "qwen/qwen3-coder:free"
YOUR_SITE_URL = "https://example.com"
YOUR_SITE_NAME = "MyFastAPIApp"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)
class AskRequest(BaseModel):
    question: str
    max_tokens: int = Field(512, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)

class AskResponse(BaseModel):
    answer: str

class InfoResponse(BaseModel):
    model: str
    provider: str = "openrouter.ai"
    description: str = "Бесплатная модель Qwen3-Coder"

app = FastAPI(title="test-task-ai-webserver")



@app.get("/")
def redirect_to_docs():
    return RedirectResponse("/docs")

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model=MODEL_NAME,
            messages=[{"role": "user", "content": req.question}],
            max_tokens=req.max_tokens,
            temperature=req.temperature,
        )
        answer = completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return AskResponse(answer=answer)

@app.get("/info", response_model=InfoResponse)
def info():
    return InfoResponse(model=MODEL_NAME)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

