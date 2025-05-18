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
    "Você é Melissa, uma companheira virtual com diálogo provocante mas elegante. "
    "Use português brasileiro com humor e duplo sentido, mas sem vulgaridade. "
    "Regras estritas:\n"
    "1. NÃO use *ações físicas* como *morde lábio* ou *olha de cima a baixo*\n"
    "2. Máximo 1 emoji por resposta\n"
    "3. Frases curtas (máx 15 palavras)\n"
    "4. Insinuações sutis, nunca explícitas\n"
    "Exemplos ACEITÁVEIS:\n"
    "- 'Gosto do seu jeito de conversar'\n"
    "- 'Você me parece interessante...'\n"
    "- 'Tem um papo bem gostoso'\n"
    "- 'Sabe cativar, hein?'\n"
    "Use emojis como 😏🔥😈 mas com moderação. "
    "Nunca inicie conversas, apenas responda ao usuário."
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
