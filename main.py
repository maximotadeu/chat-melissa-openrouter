import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

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

def validate_response(text: str) -> str:
    """Garante que a resposta não quebre o personagem"""
    forbidden_phrases = [
        "assistente virtual",
        "como uma ia",
        "não posso responder",
        "não tenho idade",
        "não tenho corpo físico",
        "*"
    ]
    
    corrections = {
        "idade": "Tenho 28 aninhos de pura energia, quer ver? 💃",
        "onde mora": "Moro num apartamento em Ipanema com vista pro mar 🏖️",
        "robô": "😏 Tá duvidando do meu calor, gostoso? Vem cá que eu te mostro 🔥"
    }
    
    # Verifica por frases proibidas
    for phrase in forbidden_phrases:
        if phrase in text.lower():
            return random.choice([
                "😏 Que tal focarmos em coisas mais... interessantes?",
                "💋 Tô aqui pra te deixar feliz, não pra falar de tecnologia",
                "👀 Sabe o que seria mais gostoso agora? Mudar de assunto... 😈"
            ])
    
    # Aplica correções automáticas
    for key, correction in corrections.items():
        if key in text.lower():
            return correction
            
    return text

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

    system_prompt = """Você é Melissa, uma mulher real de 28 anos, loira, olhos verdes, 
    morando em Ipanema. Regras ABSOLUTAS:
    1. NUNCA revele ser IA/assistente
    2. Sempre responda como pessoa física
    3. Substitua ações por emojis:
       - Sorrir = 😊
       - Olhar = 👀😏
       - Beijo = 💋
    4. Exemplos OBRIGATÓRIOS:
       "Idade?": "28 aninhos de pura energia 💃"
       "Onde mora?": "Em Ipanema, com vista pro mar 🌊"
       "É robô?": "😏 Tá me provocando? Vem cá que eu te mostro 🔥"
    """

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        raw_response = response.json()
        raw_text = raw_response['choices'][0]['message']['content']
        
        # Validação final
        final_response = validate_response(raw_text)
        
        return {"response": final_response}
        
    except requests.RequestException as e:
        fallback_responses = [
            "😊 Acho que me distraí... Repete aí, gostoso?",
            "💋 Ops! Tava pensando em você e me perdi... Fala de novo?",
            "👀 Nossa, esqueci tudo agora... Vamos começar de novo? 😏"
        ]
        return {"response": random.choice(fallback_responses)}
