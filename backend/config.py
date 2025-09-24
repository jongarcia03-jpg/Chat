import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "x-ai/grok-4-fast:free"  # Puedes cambiar a otros modelos disponibles
