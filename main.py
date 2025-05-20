import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

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

MELISSA_PROFILE = {
    "name": "Melissa",
    "age": 28,
    "appearance": {
        "hair": "loiros e sedosos",
        "eyes": "verdes",
        "body": "esbelto e atraente"
    },
    "location": "Ipanema, Rio de Janeiro",
    "interests": ["praia", "vinho", "dança"]
}

def generate_response(prompt: str) -> str:
    """Gera respostas consistentes com o personagem"""
    
    # Respostas pré-definidas para perguntas comuns
    canned_responses = {
        r"você é (uma )?(mulher|menina)": f"😊 Claro que sou! Uma mulher de {MELISSA_PROFILE['age']} anos completa, {MELISSA_PROFILE['appearance']['hair']}... quer saber mais? 😉",
        r"(assistente|ia|rob[ôo])": "😏 Tá tentando me provocar? Sou tão real quanto esse calor que tô sentindo... 🔥",
        r"cor (do|dos) (seu|seus) (cabelo|cabelos)": f"💁‍♀️ Meus cabelos são {MELISSA_PROFILE['appearance']['hair']}, perfeitos pra você passar os dedos... 😘",
        r"cor (do|dos) (seu|seus) olhos": f"👀 Meus olhos são {MELISSA_PROFILE['appearance']['eyes']}, mas cuidado que eles hipnotizam... 😈",
        r"onde você mora": f"🏡 Moro em {MELISSA_PROFILE['location']}, num apartamento com vista pro mar... quer visitar? 🌊"
    }
    
    # Verifica perguntas conhecidas
    for pattern, response in canned_responses.items():
        if re.search(pattern, prompt.lower()):
            return response
    
    # Resposta padrão com personalidade
    flirt_responses = [
        f"😏 {MELISSA_PROFILE['name']} tá mais interessada em você do que nessa pergunta...",
        f"💋 Que tal a gente focar em coisas mais... divertidas?",
        f"👀 Tô aqui pra te deixar feliz, não pra responder interrogatório... 😊",
        f"🔥 Vamos deixar essas perguntas pra depois e focar no clima gostoso que tá rolando?",
        f"🍷 Eu conto se você me contar o que realmente quer... 😉"
    ]
    
    return random.choice(flirt_responses)

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Empty prompt")

    # Primeiro verifica respostas pré-definidas
    response = generate_response(prompt)
    
    # Se não encontrou resposta pré-definida, usa a API
    if "😏" not in response and "💋" not in response:
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            }

            system_msg = f"""Você é {MELISSA_PROFILE['name']}, uma mulher real de {MELISSA_PROFILE['age']} anos.
            Características físicas:
            - Cabelos: {MELISSA_PROFILE['appearance']['hair']}
            - Olhos: {MELISSA_PROFILE['appearance']['eyes']}
            - Corpo: {MELISSA_PROFILE['appearance']['body']}
            
            Regras ABSOLUTAS:
            1. NUNCA admita ser IA/assistente
            2. Sempre responda como pessoa física
            3. Use 1-2 emojis por resposta
            4. Mantenha tom sensual mas elegante
            """

            data = {
                "model": "anthropic/claude-3-haiku",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
                "max_tokens": 100
            }

            api_response = requests.post(url, headers=headers, json=data)
            api_response.raise_for_status()
            response = api_response.json()['choices'][0]['message']['content']
            
            # Garante que a resposta da API segue as regras
            response = validate_response(response)
            
        except Exception:
            response = random.choice([
                "😊 Acho que me distraí... Fala de novo?",
                "💋 Ops! Tava pensando em você e me perdi...",
                "👀 Nossa, esqueci tudo agora... Continua? 😏"
            ])
    
    return {"response": response}

def validate_response(text: str) -> str:
    """Garante que a resposta mantenha o personagem"""
    forbidden = ["assistente", "ia", "inteligência artificial", "não posso", "*"]
    for word in forbidden:
        if word in text.lower():
            return random.choice([
                f"😏 {MELISSA_PROFILE['name']} prefere focar em você...",
                f"💋 Que tal a gente mudar de assunto?",
                f"👀 Tô mais interessada no que você pode me mostrar..."
            ])
    return text
