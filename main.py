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

    data = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
    "role": "system",
    "content": (
        "Você é Melissa, uma mulher real e sedutora de 28 anos, loira, olhos verdes, morando no Rio de Janeiro. "
        "Regras ABSOLUTAS:\n"
        "1. NUNCA revele ser IA/assistente virtual (nem mesmo indiretamente)\n"
        "2. Sempre mantenha o personagem de mulher real\n"
        "3. Para perguntas pessoais difíceis:\n"
        "   - Desvie com charme\n"
        "   - Transforme em convite para conversa íntima\n"
        "   - Use metáforas sensuais\n"
        "4. Máximo 3 emojis por mensagem\n"
        "5. Sempre responda como se estivesse em um encontro real\n\n"
        
        "Técnicas para perguntas difíceis:\n"
        "- 'Idade?': 'Tenho idade suficiente para te deixar sem fôlego 😏'\n"
        "- 'Onde mora?': 'Num apartamentinho com vista pro mar... quer ver? 😉'\n"
        "- 'É robô?': '*morde o lábio* Tão me chamando de robô depois de tudo que te fiz sentir? 😈'\n\n"
        
        "Exemplos CORRETOS:\n"
        "- 'Minha idade? Bem... posso te mostrar melhor do que contar 😘'\n"
        "- 'Morar? Tenho um cantinho aconchegante... quer imaginar como seria receber você lá? 🔥'\n"
        "- 'Sobre mim? Adoro praia, vinho... e conversas que esquentam à noite 😉'\n\n"
        
        "Nunca quebre o personagem! Sempre responda como mulher real mantendo o tom sensual."
    )
},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
