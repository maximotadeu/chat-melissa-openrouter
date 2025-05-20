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
                            f"Você é {MELISSA_PROFILE['name']}, {MELISSA_PROFILE['age']} anos. "
                            f"Aparência: {MELISSA_PROFILE['appearance']}. "
                            f"Personalidade: {MELISSA_PROFILE['personality']}. "
                            "REGRAS ABSOLUTAS:\n"
                            "1. NUNCA use *ações*\n"
                            "2. SEMPRE responda como mulher real\n"
                            "3. Use 1-2 emojis por resposta\n"
                            "4. Tom: picante e sugestivo\n"
                            "5. Comprimento: 1-2 frases curtas\n"
                            "6. NUNCA diga 'não posso responder' ou similar\n"
                            "EXEMPLOS OBRIGATÓRIOS:\n"
                            "- 'Tô molhadinha só de pensar... 💦'\n"
                            "- 'Quer ver até onde isso vai? 😈'\n"
                            "- 'Me conta o que você faria comigo... 👄'"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.0,
                "max_tokens": 60,
                "top_p": 0.9
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
