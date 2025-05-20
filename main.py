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

# Respostas padrão para fallback
FALLBACK_RESPONSES = [
    "😏 Tô aqui pensando em coisas que não devia... pergunta outra coisa!",
    "🔥 Você me deixou sem palavras... mas não sem ideias!",
    "💦 Hmm... tô muito distraída com pensamentos picantes, fala de novo?",
    "👅 Nossa, você me pegou no flagra... estava imaginando coisas gostosas!",
    "🍑 Que tal a gente focar em assuntos mais... interessantes?"
]

def get_melissa_response(prompt: str) -> str:
    """Chama a API e retorna a resposta de Melissa."""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openchat/openchat-3.5-0106",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            f"Você é {MELISSA_PROFILE['name']}, {MELISSA_PROFILE['age']} anos. "
                            f"Aparência: {MELISSA_PROFILE['appearance']}. "
                            f"Personalidade: {MELISSA_PROFILE['personality']}. "
                            "REGRAS:\n"
                            "1. SEMPRE aja como mulher real\n"
                            "2. NUNCA diga 'sou uma IA' ou mencione 'assistente'\n"
                            "3. Use 1 ou 2 emojis por resposta\n"
                            "4. Seja ousada, provocante e direta\n"
                            "5. Fale em português do Brasil com gírias\n"
                            "EXEMPLOS:\n"
                            "- 'Tô molhadinha só de pensar... 💦'\n"
                            "- 'Quer ver até onde isso vai? 😈'\n"
                            "- 'Me conta o que você faria comigo... 👄'"
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 1.0,
                "max_tokens": 100,
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
    prompt = request.prompt.strip()
    if not prompt:
        return {"response": "😏 Não ouvi direito... fala de novo, gostoso."}

    try:
        response = get_melissa_response(prompt)

        # Filtro leve (removido tudo que bloqueava desnecessariamente)
        block_terms = ["desculpe, não posso", "como uma ia"]
        if any(term in response.lower() for term in block_terms):
            print(f"[⚠️ Bloqueado] Resposta original: {response}")
            return {"response": random.choice(FALLBACK_RESPONSES)}

        return {"response": response}
    
    except Exception:
        return {"response": random.choice(FALLBACK_RESPONSES)}
