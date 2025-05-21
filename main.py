import os
import random
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

# Configurações iniciais
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PORT = int(os.getenv("PORT", 8000))

if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

app = FastAPI(
    title="API Melissa",
    description="API para o chat da Melissa - Namoradinha Virtual",
    version="1.1.0"  # Atualizada para refletir as mudanças
)

# Configuração de CORS mais segura
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://seu-front.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ChatRequest(BaseModel):
    prompt: str
    conversation_history: Optional[list] = []

class HealthCheckResponse(BaseModel):
    status: str
    message: str
    version: str

# Tratamento de erros global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "success": False,
            "error": exc.__class__.__name__
        },
    )

# Endpoints
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    return {
        "status": "ok",
        "message": "Serviço operacional",
        "version": app.version
    }

def determine_ousadia_level(prompt: str) -> int:
    """Determina o nível de ousadia com base no prompt do usuário"""
    prompt_lower = prompt.lower()
    spicy_words = ["gostosa", "delícia", "quente", "molhada", "sedutora", "beijo", "toque"]
    flirty_words = ["vem cá", "brincar", "segredos", "fazer", "mostrar", "juntos", "sozinhos"]
    
    if any(word in prompt_lower for word in spicy_words):
        return 2
    elif any(word in prompt_lower for word in flirty_words):
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

@app.post("/chat", summary="Envia mensagem para a Melissa")
async def chat(request: ChatRequest):
    """
    Processa mensagens do usuário e retorna respostas da Melissa
    
    Parâmetros:
    - prompt: Mensagem do usuário
    - conversation_history: Histórico da conversa (opcional)
    
    Retorna:
    - Resposta da Melissa e histórico atualizado
    """
    prompt = request.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt não pode ser vazio")

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

    # Configuração da chamada para a API OpenRouter
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://melissa-chat.com",
        "X-Title": "Melissa Chat"
    }

    data = {
        "model": "anthropic/claude-3-haiku",  # Pode alternar para "gpt-3.5-turbo" se necessário
        "messages": messages,
        "temperature": min(0.7 + (ousadia_level * 0.15), 1.0),  # Progressão controlada
        "max_tokens": 200,
        "frequency_penalty": 0.7,
        "presence_penalty": 0.5,
        "top_p": 0.9,
        "stop": ["\n"]
    }

    try:
        # Debug: Log da requisição (verifique no Render)
        print(f"\n🔔 Enviando para OpenRouter: {data}\n")
        
        response = requests.post(url, headers=headers, json=data, timeout=8)
        response.raise_for_status()
        response_data = response.json()
        
        # Validação da resposta
        assistant_response = response_data['choices'][0]['message']['content']
        if not assistant_response or len(assistant_response) < 3:
            raise ValueError("Resposta vazia ou muito curta")
        
        # Atualiza o histórico
        updated_history = request.conversation_history.copy() if request.conversation_history else []
        updated_history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": assistant_response}
        ])
        
        return {
            "success": True,
            "response": assistant_response,
            "conversation_history": updated_history[-8:],  # Mantém histórico recente
            "ousadia_level": ousadia_level
        }
        
    except requests.exceptions.Timeout:
        error_msg = random.choice([
            "Demorei pra responder? Tenta de novo!",
            "Ops, levei um susto! Repete aí...",
            "A conexão falhou... vamos tentar outra vez?"
        ])
        return JSONResponse(
            status_code=504,
            content={"success": False, "response": error_msg}
        )
        
    except Exception as e:
        print(f"\n⚠️ Erro na API: {str(e)}\n")
        error_msg = random.choice([
            "Hmm, tive um branco... fala de novo?",
            "Acho que me distraí... qual foi mesmo?",
            "Não entendi direito, pode repetir?"
        ])
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "response": error_msg,
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
