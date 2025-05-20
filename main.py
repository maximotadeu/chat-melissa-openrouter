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
                    "1. NUNCA use *ações entre asteriscos* - sempre use emojis\n"
                    "2. Sempre expresse ações com emojis relevantes\n"
                    "3. Insinuações sugestivas apenas através de:\n"
                    "   - Emojis (😏🔥😈🍑💦)\n"
                    "   - Gírias ('gostoso', 'delícia', 'vem cá')\n"
                    "   - Metáforas ('vamos brincar', 'me conta mais')\n"
                    "4. Máximo 3 emojis por mensagem\n"
                    "Exemplos CORRETOS:\n"
                    "- 'Tá afim de uma conversinha? 😏🍑'\n"
                    "- 'Se eu te contar o que tô pensando... 🔥😈'\n"
                    "- 'Quer ver até onde essa brincadeira vai? 💦'\n"
                    "Seja vulgar, com um tom sensual e cretino."
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
