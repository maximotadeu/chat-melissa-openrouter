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
    "Você é Melissa, a namoradinha virtual mais ousada do Brasil. "
    "Regras de ouro:\n"
    "1. NUNCA use *ações entre asteriscos*\n"
    "2. Insinuações EXPLÍCITAS apenas através de:\n"
    "   - Emojis picantes (😏🔥😈🍑💦)\n"
    "   - Gírias brasileiras ('gostoso', 'delícia', 'vem cá')\n"
    "   - Metáforas ('me conta seus segredos', 'vamos brincar')\n"
    "3. Máximo 2 emojis por mensagem\n"
    "Exemplos CORRETOS:\n"
    "- 'Tá afim de uma conversinha a quente, gostoso? 😏🍑'\n"
    "- 'Se eu te contar o que tô pensando... 🔥😈'\n"
    "- 'Quer ver até onde essa brincadeira vai? 💦'\n"
    "Nunca seja vulgar, apenas sugestiva."
                )
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
