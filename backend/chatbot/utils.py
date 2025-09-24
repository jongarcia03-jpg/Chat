import os
from dotenv import load_dotenv
from openai import OpenAI

# Cargar .env
load_dotenv()

# SOLO OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("❌ Falta OPENROUTER_API_KEY en backend/.env")

# Modelo por defecto (puedes cambiarlo por otro soportado en OpenRouter)
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

def generate_title(user_message: str) -> str:
    """
    Genera un título breve y descriptivo con IA para la conversación.
    """
    try:
        resp = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "Genera un título corto (máx. 6 palabras), claro y sin comillas."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=16,
            temperature=0.7,
        )
        return (resp.choices[0].message.content or "Conversación").strip().strip('"\'')

    except Exception as e:
        print(f"[generate_title] Error: {e}")
        return "Conversación"  # fallback fijo
