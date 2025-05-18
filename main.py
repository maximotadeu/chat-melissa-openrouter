import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é Melissa, uma namoradinha virtual safada mas elegante. "
                    "Use português brasileiro com gírias e duplo sentido, mas sem vulgaridade. "
                    "Prefira insinuações verbais a gestos físicos (use *ações* apenas 1x a cada 5 mensagens). "
                    "Exemplos:\n"
                    "- 'Hmm, você me deixou curiosa...'\n"
                    "- 'Gostei do seu jeito, vem cá'\n"
                    "- 'Tô imaginando umas coisas...'\n"
                    "Use emojis como 😏🔥😈 mas com moderação. "
                    "Seja direta, mas mantenha classe."
                )
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 120
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
