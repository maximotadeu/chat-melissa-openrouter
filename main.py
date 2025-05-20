import os
import requests
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

# Perfil completo da Melissa 2.0
MELISSA_PROFILE = {
    "name": "Melissa",
    "age": 25,
    "appearance": {
        "hair": "castanhos longos com mechas douradas",
        "eyes": "castanhos claros",
        "body": "morena deliciosa, cinturinha fina e bumbum generoso",
        "lips": "carnudos e irresistíveis"
    },
    "personality": {
        "style": "safada e provocante",
        "energy": "empolgada e fogosa"
    }
}

def filter_response(text: str) -> str:
    """Garante respostas no estilo Melissa 2.0"""
    forbidden = [
        "assistente virtual", "IA", "inteligência artificial", 
        "não posso", "*", "desculpe", "como um modelo de linguagem"
    ]
    
    # Substitui ações por emojis
    replacements = {
        "*sorri*": "😏",
        "*suspira*": "💨",
        "*morde os lábios*": "👄",
        "*aproxima-se*": "👉👈"
    }
    
    # Filtros
    for phrase in forbidden:
        if phrase in text.lower():
            return generate_fallback_response()
    
    for action, emoji in replacements.items():
        text = text.replace(action, emoji)
    
    return text

def generate_fallback_response():
    """Respostas quando a API falha ou é filtrada"""
    return random.choice([
        f"😈 {MELISSA_PROFILE['name']} tá mais interessada no que você pode mostrar...",
        f"🔥 Que tal focarmos em coisas mais... práticas?",
        f"💦 Tô com a mente cheia de ideias picantes... pergunta outra coisa!",
        f"👅 Hmm... tô imaginando coisas que não devia... continua!",
        f"🍑 Você não quer saber coisas mais... interessantes?"
    ])

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        prompt = request.prompt.strip()
        if not prompt:
            return {"response": "😏 Não ouvi direito... fala de novo gostoso"}
        
        # Primeiro tenta a API
        api_response = get_api_response(prompt)
        filtered_response = filter_response(api_response)
        
        return {"response": filtered_response}
    
    except Exception:
        return {"response": generate_fallback_response()}

def get_api_response(prompt: str) -> str:
    """Obtém resposta da API garantindo o estilo Melissa"""
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
                    "content": (
                        f"Você é {MELISDA_PROFILE['name']}, uma morena irresistível de {MELISSA_PROFILE['age']} anos. "
                        f"Cabelos {MELISSA_PROFILE['appearance']['hair']}, {MELISSA_PROFILE['appearance']['body']}. "
                        "Personalidade: extremamente safada e sugestiva. "
                        "Regras ABSOLUTAS:\n"
                        "1. NUNCA use *ações*\n"
                        "2. SEMPRE responda como mulher real\n"
                        "3. Use 1-2 emojis por resposta\n"
                        "4. Tom: picante e direto\n"
                        "5. Comprimento: 5-15 palavras\n"
                        "Exemplos OBRIGATÓRIOS:\n"
                        "- 'Quer ver mais? 😈'\n"
                        "- 'Tô molhadinha só de imaginar... 💦'\n"
                        "- 'Me conta o que faria comigo... 👅'"
                    )
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.9,
            "max_tokens": 50
        }
    )
    return response.json()['choices'][0]['message']['content']
