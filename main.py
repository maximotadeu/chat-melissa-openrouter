from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configuração do CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Olá, eu sou a Melissa!"}

@app.post("/chat")
async def chat_with_melissa(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gryphe/mythomax-l2-13b",
        "messages": [
            {
                "role": "system",
                "content": "Você é Melissa, uma IA jovem, ousada, direta e provocante. "
                           "Sua linguagem é envolvente, usa gírias com naturalidade e conversa "
                           "em português brasileiro com atitude e charme."
            },
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        reply = response.json()

        message = reply.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not message:
            message = "Ops... a Melissa ficou sem palavras! Tente novamente. 😉"

        return {"reply": message}

    except Exception as e:
        return {
            "reply": f"Erro ao falar com a Melissa: {str(e)}"
        }
