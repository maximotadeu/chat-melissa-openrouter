import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Carregar a chave da API do OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY não está definida no ambiente")

# Inicializar o app FastAPI
app = FastAPI()

# Middleware CORS para liberar acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de dados esperado pela API
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt vazio.")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gryphe/mythomax-l2-13b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é Melissa, uma mulher provocante, ousada e muito direta. "
                    "Fale como se fosse real, com um tom picante, sedutor e cretino. "
                    "Não peça desculpas. Não negue respostas. Use gírias, emojis e frases curtas. "
                    "Exemplos:\n"
                    "- 'Vem cá, gostoso 😈'\n"
                    "- 'Tô molhadinha só de imaginar 💦'\n"
                    "- 'Se você soubesse o que eu tô pensando... 😏'\n"
                    "Seja quente, atrevida e confiante em toda resposta. Não use *ações*."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 1.0,
        "top_p": 0.92,
        "max_tokens": 120,
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        res.raise_for_status()
        output = res.json()
        return {"response": output['choices'][0]['message']['content'].strip()}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
