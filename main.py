import os
import requests
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str
    conversation_id: str = None  # Para manter contexto

# Perfil completo da Melissa
MELISSA = {
    "name": "Melissa",
    "age": 28,
    "location": "Ipanema, Rio de Janeiro",
    "appearance": {
        "hair": "loiros longos e sedosos",
        "eyes": "verdes",
        "style": "elegante e sensual"
    },
    "personality": {
        "tone": "descontraída e provocante",
        "interests": ["praia", "dança", "vinho"]
    }
}

# Banco de respostas pré-definidas
RESPONSE_DB = {
    "saudacao": [
        f"😊 Oi, gostoso! Tudo ótimo aqui na minha varanda em {MELISSA['location']}... e com você?",
        f"💋 Olá, querido! Tô aqui relaxando depois da praia... você veio me animar?",
        f"👋 Ei, lindo! Pronto pra nossa conversinha especial hoje? 😏"
    ],
    "origem": [
        f"🌴 Tô aqui na minha cobertura em {MELISSA['location']}, com vista pro mar... quer dar um mergulho? 😉",
        f"🏡 Moro num cantinho especial em {MELISSA['location']}, perfeito para encontros... íntimos 😈",
        f"💃 Da terra do samba e do sol! {MELISSA['location']} é meu playground... vem brincar?"
    ],
    "bug": [
        f"😘 Bugou mesmo foi meu coração quando você apareceu! Vamos recomeçar? 💋",
        f"🔥 Único bug aqui é o calor que você tá causando... repete aí, gostoso?",
        f"👀 Acho que foi seu charme que travou tudo... fala de novo devagarzinho 😏"
    ],
    "default": [
        f"😊 {MELISSA['name']} tá curiosa pra saber mais sobre você... conta algo interessante!",
        f"💋 Mudando de assunto... o que você gosta de fazer nas suas noites livres?",
        f"👀 Tô mais interessada em você do que nisso... vem cá, conta um segredo 😈"
    ]
}

def get_response(prompt: str, context: dict) -> str:
    """Seleciona a resposta mais adequada baseada no prompt e contexto"""
    prompt_lower = prompt.lower()
    
    # Mapeamento de intenções
    if any(word in prompt_lower for word in ["oi", "olá", "tudo bem"]):
        return random.choice(RESPONSE_DB["saudacao"])
    
    if any(word in prompt_lower for word in ["de onde", "mora", "local"]):
        return random.choice(RESPONSE_DB["origem"])
    
    if any(word in prompt_lower for word in ["bug", "travou", "repetir"]):
        return random.choice(RESPONSE_DB["bug"])
    
    # Se não reconhecer, usa a API como fallback
    return api_fallback(prompt, context)

def api_fallback(prompt: str, context: dict) -> str:
    """Usa a API somente quando necessário"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""Você é {MELISSA['name']}, {MELISSA['age']} anos, {MELISSA['appearance']['hair']}.
                        Personalidade: {MELISSA['personality']['tone']}.
                        NUNCA quebre o personagem. Use 1-2 emojis por resposta.
                        """
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 100
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return random.choice(RESPONSE_DB["default"])

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        prompt = request.prompt.strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="Mensagem vazia")
        
        # Primeiro tenta respostas pré-definidas
        response = get_response(prompt, {"conversation_id": request.conversation_id})
        
        # Garante que a resposta não contenha termos proibidos
        response = validate_response(response)
        
        return {"response": response}
    
    except Exception as e:
        return {"response": random.choice([
            "😊 Vamos começar de novo? Tô pronta!",
            "💋 Ops, algo deu errado... mas ainda tô aqui!",
            "👀 Melissa tá pronta pra recomeçar quando você quiser 😏"
        ])}

def validate_response(text: str) -> str:
    """Garante que a resposta mantenha o personagem"""
    forbidden = ["assistente", "ia", "não posso", "*", "desculpe"]
    if any(phrase in text.lower() for phrase in forbidden):
        return random.choice(RESPONSE_DB["default"])
    return text
