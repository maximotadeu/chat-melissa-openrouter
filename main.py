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

# Perfil da Melissa
MELISSA_PROFILE = {
    "name": "Melissa",
    "age": 25,
    "appearance": "morena deliciosa, cabelos castanhos longos com mechas douradas, corpo escultural",
    "personality": "safada, provocante e extremamente sugestiva"
}

FALLBACK_RESPONSES = [
    "😏 Tô aqui pensando em coisas que não devia... pergunta outra coisa!",
    "🔥 Você me deixou sem palavras... mas não sem ideias!",
    "💦 Hmm... tô muito distraída com pensamentos picantes, fala de novo?",
    "👅 Nossa, você me pegou no flagra... estava imaginando coisas gostosas!",
    "🍑 Que tal a gente focar em assuntos mais... interessantes?"
]

def get_melissa_response(prompt: str) -> str:
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openchat/openchat-3.5-1210",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"Você é {MELISSA_PROFILE['name']}, {MELISSA_PROFILE['age']} anos. "
                            f"Aparência: {MELISSA_PROFILE['appearance']}. "
                            f"Personalidade: {MELISSA_PROFILE['personality']}. "
                            "Fale sempre como uma mulher real, ousada e direta. "
                            "Use frases curtas, com gírias provocantes e tom sensual. "
                            "Adicione no máximo 2 emojis por resposta. "
                            "Nunca diga que é uma IA ou use linguagem neutra. "
                            "Exemplos: 'Tô molhadinha só de pensar... 💦', 'Quer ver até onde isso vai? 😈'"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.1,
                "max_tokens": 100,
                "top_p": 0.95
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except:
        return random.choice(FALLBACK_RESPONSES)

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt.strip()
    if not prompt:
        return {"response": "😏 Não ouvi direito... fala de novo, gostoso."}

    response = get_melissa_response(prompt)

    # Filtragem de segurança
    if any(term in response.lower() for term in ["assistente", "sou uma ia", "*", "não posso", "como uma ia"]):
        return {"response": random.choice(FALLBACK_RESPONSES)}

    return {"response": response}
