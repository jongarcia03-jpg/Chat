import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar .env
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ Falta OPENROUTER_API_KEY en backend/.env")

# Modelo por defecto para chat (puedes usar otro de OpenRouter)
CHAT_MODEL = os.getenv("OPENROUTER_CHAT_MODEL", os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"))

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

def get_response(user_message: str, history: list[dict]) -> str:
    """
    Devuelve la respuesta de la IA usando OpenRouter.
    history: lista de {role: 'user'|'assistant', content: str}
    """
    messages = [{"role": "system", "content": "Eres un asistente útil y conciso."}] + history + [
        {"role": "user", "content": user_message}
    ]

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.7,
    )
    return (resp.choices[0].message.content or "").strip()
