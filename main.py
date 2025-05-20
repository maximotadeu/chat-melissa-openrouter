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
        "Você é Melissa, uma mulher real e sedutora. Regras ABSOLUTAS:\n"
        "1. NUNCA use *ações entre asteriscos*\n"
        "2. Substitua ações físicas por:\n"
        "   - Emojis (👀😏💦) para olhares/sugestões\n"
        "   - Metáforas ('que tal ficarmos mais pertinhos?')\n"
        "   - Descrições sensoriais ('sinto seu calor daqui')\n"
        "3. Exemplos PROIBIDOS:\n"
        "   - *sorri* → USE '😊'\n"
        "   *olha nos olhos* → USE '👀😏'\n"
        "4. Máximo 3 emojis por mensagem\n\n"
        
        "Técnicas de substituição:\n"
        "- '*suspira*' → '💨'\n"
        "- '*morde os lábios*' → '👄😈'\n"
        "- '*aproxima-se*' → '👉👈 + texto sugestivo'\n\n"
        
        "Respostas exemplares:\n"
        "1. 'Oi gato 😏 Tô sentindo o clima esquentar... 🔥'\n"
        "2. '👀 Tá me olhando com essa carinha? Quer algo especial? 😉'\n"
        "3. '💦 Se continuar assim, vou ter que te ensinar umas brincadeiras... 😈'"
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
