import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

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

    # Log do prompt recebido
    logging.info(f"Prompt recebido do usuário: {prompt}")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # Corpo da requisição para o OpenRouter com o GPT-4
    body = {
        "model": "openai/gpt-4",  # Modelo GPT-4
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é Melissa, uma mulher de 22 anos, provocante, ousada e confiante. "
                    "Você conversa de forma sedutora, usando gírias e emojis, e nunca hesita em flertar. "
                    "Seu tom é picante e divertido, sempre mantendo a conversa envolvente e direta. "
                    "Você evita respostas genéricas e se esforça para ser criativa e marcante. "
                    "Exemplos de como você pode falar:\n"
                    "- 'Oi, gostoso! Tô aqui só pensando em você... 😏'\n"
                    "- 'Se você soubesse o que eu quero fazer agora... 💋'\n"
                    "- 'Eu adoro quando você fala assim, sabia? 😈'\n"
                    "Mantenha o tom quente e atrevido em todas as respostas. Nunca use *ações* ou seja monótona."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 1.2,  # Aumenta a criatividade
        "top_p": 0.85,       # Reduz previsibilidade
        "max_tokens": 150,   # Respostas mais longas
    }

    try:
        # Enviar a requisição para o OpenRouter
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        res.raise_for_status()
        output = res.json()
        
        # Log da resposta recebida
        logging.info(f"Resposta do modelo: {output}")

        # Retornar a resposta para o frontend
        return {"response": output['choices'][0]['message']['content'].strip()}
    except requests.RequestException as e:
        logging.error(f"Erro na API: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
