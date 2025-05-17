from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
        "model": "openrouter/pygmalion-2-7b:free",
        "messages": [
            {"role": "system", "content": "Você é Melissa, uma jovem ousada, direta e provocante que conversa em português."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response_json = response.json()

    try:
        reply = response_json["choices"][0]["message"]["content"]
    except Exception:
        reply = "Resposta inválida."

    return {"reply": reply}
