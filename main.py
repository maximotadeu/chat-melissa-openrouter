from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Permitir CORS para seu frontend (pode colocar o domínio específico depois)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ideal trocar por lista do front em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Olá, eu sou a Melissa!"}

@app.post("/chat")
async def chat_with_melissa(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")
        print(f"[DEBUG] Prompt recebido: {prompt}")

        if not prompt.strip():
            return {"reply": "Por favor, envie uma mensagem válida."}

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        data = {
            # Coloque aqui o modelo correto que você vai usar, verifique na doc do OpenRouter.
            "model": "openrouter/pygmalion-2-7b:free",
            "messages": [
                {
                    "role": "system",
                    "content": "Você é Melissa, uma jovem ousada, direta e provocante que conversa em português."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        print(f"[DEBUG] Status da resposta OpenRouter: {response.status_code}")
        print(f"[DEBUG] Conteúdo da resposta OpenRouter: {response.text}")

        response.raise_for_status()  # levanta erro para status >= 400

        response_json = response.json()
        # Pega o conteúdo da resposta na estrutura esperada
        reply = response_json["choices"][0]["message"]["content"]
        print(f"[DEBUG] Reply extraído: {reply}")

        return {"reply": reply}

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Erro na requisição para OpenRouter: {e}")
        return {"reply": "Erro na comunicação com o serviço de IA."}
    except (KeyError, IndexError, ValueError) as e:
        print(f"[ERROR] Erro ao processar a resposta da API: {e}")
        return {"reply": "Resposta inválida da API."}
    except Exception as e:
        print(f"[ERROR] Erro inesperado: {e}")
        return {"reply": "Erro inesperado no servidor."}
