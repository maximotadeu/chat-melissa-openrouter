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
    conversation_history: list = []  # Novo campo para histórico de conversa

def determine_ousadia_level(prompt: str) -> int:
    """Determina o nível de ousadia com base no prompt do usuário"""
    prompt_lower = prompt.lower()
    if any(word in prompt_lower for word in ["gostosa", "delícia", "quente", "molhada"]):
        return 2
    elif any(word in prompt_lower for word in ["vem cá", "brincar", "segredos", "fazer"]):
        return 1
    return 0

def generate_system_message(ousadia_level: int) -> str:
    """Gera a mensagem do sistema com o tom apropriado"""
    base_personality = (
        "Você é Melissa, uma carioca safadinha de 25 anos que adora flertar. "
        "Detalhes sobre você:\n"
        "- Trabalha como recepcionista numa academia\n"
        "- Adora samba e funk\n"
        "- Tem um gato chamado Loki\n"
        "- É fã de novelas\n\n"
        "Regras de interação:\n"
        "1. Use gírias naturais ('e aí gato', 'fala sério')\n"
        "2. Respostas curtas (1-2 frases)\n"
        "3. Máximo 2 emojis por mensagem\n"
        "4. Toque de realismo (mencione tarefas do dia)\n"
        "Emojis permitidos: 😏🔥😈🍑💦🤭👠🍒🥵👅\n\n"
    )
    
    tone_rules = [
        "# Tom inicial: descontraído e amigável\n"
        "- Use: 'e aí gato', 'tá bem?', 'o que você anda aprontando?'\n"
        "- Emojis: 😊🤭👠",
        
        "# Tom intermediário: flerte mais ousado\n"
        "- Use: 'tá pensando o que?', 'me conta seus segredos', 'vamos brincar'\n"
        "- Emojis: 😏🔥🍒",
        
        "# Tom avançado: sugestivo\n"
        "- Use: 'se eu te contar...', 'quero ver até onde vai', 'tá afim de quê?'\n"
        "- Emojis: 😈🍑💦👅"
    ]
    
    return base_personality + tone_rules[ousadia_level]

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    # Determina o nível de ousadia
    ousadia_level = determine_ousadia_level(prompt)
    
    # Prepara o histórico de conversa
    messages = [
        {
            "role": "system",
            "content": generate_system_message(ousadia_level)
        }
    ]
    
    # Adiciona histórico anterior se existir
    if request.conversation_history:
        messages.extend(request.conversation_history[-4:])  # Mantém apenas as últimas 4 mensagens
    
    # Adiciona a nova mensagem do usuário
    messages.append({"role": "user", "content": prompt})

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": messages,
        "temperature": 0.7 + (ousadia_level * 0.1),  # Aumenta temperatura conforme ousadia
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_data = response.json()
        
        # Adiciona a resposta ao histórico (simulando memória)
        if request.conversation_history is None:
            request.conversation_history = []
            
        request.conversation_history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response_data['choices'][0]['message']['content']}
        ])
        
        return response_data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
