import json
import os
from chatbot.memory import ChatMemory

SAVE_FILE = "conversations.json"

def save_conversations(conversations):
    data = {
        cid: {
            "title": conv["title"],
            "history": conv["memory"].get_history()
        }
        for cid, conv in conversations.items()
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_conversations():
    conversations = {}
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        conversations = {
            cid: {
                "title": conv["title"],
                "memory": ChatMemory()
            }
            for cid, conv in data.items()
        }
        for cid, conv in data.items():
            conversations[cid]["memory"].history = conv["history"]
    return conversations
