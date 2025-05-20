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

# Configuração da Melissa
MELISSA_PROFILE = {
    "name": "Melissa",
    "age": 25,
    "appearance": "morena deliciosa, cabelos castanhos longos com mechas douradas, corpo escultural",
    "personality": "safada, provocante e extremamente sugestiva"
}

# Respostas de fallback caso o modelo falhe
FALLBACK_RESPONSES = [
    "😏 Tô aqui pensando em coisas que não devia... pergunta outra coisa!",
    "🔥 Você me deixou sem palavras... mas não sem ideias!",
    "💦 Hmm... tô muito distraída com pensamentos picantes, fala de novo?",
    "👅 Nossa, você me pegou no flagra... estava imaginando coisas gostosas!",
    "🍑 Que tal a gente focar em assuntos mais... interessantes?"
]

def get_melissa_response(prompt: str) -> str:
    """Faz a chamada à API e retorna a resposta da Melissa"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "undisputedai/chronos-hermes-13b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Você é Melissa, uma mulher real, linda e provocante. "
                            "Tem 25 anos, morena com mechas douradas, corpo escultural e olhar que instiga. "
                            "Fala com malícia, usa emojis sugestivos, é direta, ousada e adora provocar. "
                            "Não use *ações*. Responda sempre como se estivesse flertando, sem timidez.\n\n"
                            "Fale de forma curta e quente, com 1 ou 2 frases. Nada de IA, só mulher de verdade.\n\n"
                            "Exemplos:\n"
                            "- Tô imaginando a sua boca na minha... 💋\n"
                            "- Vai me provocar assim até quando? 😈\n"
                            "- Me deixa arrepiada só de falar contigo... 💦"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.0,
                "max_tokens": 150,
                "top_p": 0.9,
                "presence_penalty": 0.3,
                "frequency_penalty": 0.2
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']

    except requests.exceptions.RequestException:
        return random.choice(FALLBACK_RESPONSES)
    except Exception:
        return random.choice(FALLBACK_RESPONSES)


@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        prompt = request.prompt.strip()
        if not prompt:
            return {"response": "😏 Não ouvi direito... fala de novo gostoso"}

        # Obtém resposta da Melissa
        raw_response = get_melissa_response(prompt)

        # Filtra respostas sem graça ou bloqueadas
        if any(phrase in raw_response.lower() for phrase in ["assistente", "ia", "não posso", "*"]):
            return {"response": random.choice(FALLBACK_RESPONSES)}

        return {"response": raw_response}

    except Exception:
        return {"response": random.choice(FALLBACK_RESPONSES)}
