from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

app = FastAPI()

# Permitir requisições de qualquer origem
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
def chat_with_melissa(message: dict):
    prompt = message.get("prompt", "")
    
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openrouter/pygmalion-2-7b",
        "messages": [
            {"role": "system", "content": "Você é Melissa, uma jovem ousada e provocante que conversa em português."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    return response.json()
