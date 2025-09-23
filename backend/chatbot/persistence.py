import json, os

DATA_FILE = "conversations.json"

def save_conversations(conversations):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {cid: {"title": conv["title"], "history": conv["memory"].get_history()} for cid, conv in conversations.items()},
            f,
            ensure_ascii=False,
            indent=2
        )

def load_conversations():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        from chatbot.memory import ChatMemory
        conversations = {}
        for cid, conv in raw.items():
            m = ChatMemory()
            m.history = conv.get("history", [])
            conversations[cid] = {"title": conv["title"], "memory": m}
        return conversations
