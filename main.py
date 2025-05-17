@app.post("/chat")
async def chat_with_melissa(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    print(f"Recebido prompt: {prompt}")

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/pygmalion-2-7b:free",
        "messages": [
            {"role": "system", "content": "Você é Melissa, uma jovem ousada, direta e provocante que conversa em português."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    print(f"Status da API: {response.status_code}")
    print(f"Resposta da API: {response.text}")

    try:
        response_json = response.json()
        reply = response_json["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Erro ao ler resposta: {e}")
        reply = "Resposta inválida."

    print(f"Respondendo: {reply}")

    return {"reply": reply}
