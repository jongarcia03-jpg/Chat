import json
import os

DATA_FILE = "conversations.json"

def save_conversations(conversations: dict):
    """Guarda todas las conversaciones en el archivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)

def load_conversations() -> dict:
    """Carga todas las conversaciones desde el archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ==== Nuevas funciones para integrarse con bot.py ====

def save_conversation(token: str, conv_id: str, conv_data: dict):
    """Guarda una conversación concreta asociada a un token."""
    conversations = load_conversations()
    if token not in conversations:
        conversations[token] = {}
    conversations[token][conv_id] = conv_data
    save_conversations(conversations)

def load_conversation(token: str, conv_id: str) -> dict:
    """Carga una conversación concreta asociada a un token."""
    conversations = load_conversations()
    return conversations.get(token, {}).get(conv_id, {})

def list_conversations(token: str) -> dict:
    """Devuelve todas las conversaciones de un usuario (por token)."""
    conversations = load_conversations()
    return conversations.get(token, {})

def delete_conversation(token: str, conv_id: str):
    """Elimina una conversación concreta de un usuario."""
    conversations = load_conversations()
    if token in conversations and conv_id in conversations[token]:
        del conversations[token][conv_id]
        save_conversations(conversations)
