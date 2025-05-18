import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("A variável OPENROUTER_API_KEY não está configurada.")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ajuste isso em produção
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
        raise HTTPException(status_code=400, detail="Prompt vazio")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
    "model": "anthropic/claude-3-haiku",  # Ou outro modelo da lista acima
    "messages": [
        {
            "role": "system",
            "content": (
                "Você é Melissa, a namoradinha mais safadinha e provocante do Brasil. "
                "Fala com muita malícia, gírias e duplo sentido, mas sem ser vulgar. "
                "Chama o usuário de 'gostoso', 'delícia' ou 'travesso'. "
                "Respostas curtas, diretas e cheias de emojis picantes. 😏🔥 "
                "Exemplo: 'Hmm, adivinha o que tô pensando...' *morde o lábio*"
            ),
        },
        {"role": "user", "content": prompt},
    ],
    "max_tokens": 120,  # Reduza para respostas mais curtas e baratas
    "temperature": 0.8,  # Mais criativo (aumente para 1.0 se quiser mais ousadia)
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.HTTPError as e:
        detail = f"Erro na API OpenRouter: {e.response.status_code} - {e.response.text}"
        raise HTTPException(status_code=500, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resp_json = response.json()
    return resp_json
