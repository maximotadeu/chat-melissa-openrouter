import os
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Variável de ambiente com sua API Key OpenRouter (configure no ambiente de deploy)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError("A variável OPENROUTER_API_KEY não está configurada.")

app = FastAPI()

# Permite conexões do front-end (ajuste o origin conforme seu front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mude para seu domínio em produção
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
        "Content-Type": "application/json"
    }

    data = {
        "model": "gryphe/mythomax-l2-13b",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é Melissa, uma IA jovem, ousada, direta e provocante. "
                    "Sua linguagem é envolvente, usa gírias com naturalidade e conversa "
                    "em português brasileiro com atitude e charme."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
    except requests.HTTPError as e:
        # Retorna mensagem detalhada para facilitar debugging no front-end
        detail = f"Erro na API OpenRouter: {e.response.status_code} - {e.response.text}"
        raise HTTPException(status_code=500, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resp_json = response.json()

    # Exemplo básico de extração da resposta da IA, ajuste conforme estrutura real da API
    try:
        answer = resp_json["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise HTTPException(status_code=500, detail="Resposta inválida da API OpenRouter.")

    return {"response": answer}
