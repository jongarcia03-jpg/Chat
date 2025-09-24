import uuid

class Memory:
    def __init__(self):
        # conversations[token][conv_id] = [ {role, content}, ... ]
        self.conversations: dict[str, dict[str, list[dict]]] = {}
        # active[token] = conv_id
        self.active: dict[str, str] = {}

    def start_conversation(self, token: str) -> str:
        """Crea una nueva conversación vacía para un usuario y la activa."""
        conv_id = str(uuid.uuid4())
        if token not in self.conversations:
            self.conversations[token] = {}
        self.conversations[token][conv_id] = []
        self.active[token] = conv_id
        return conv_id

    def get_active_conversation(self, token: str) -> str | None:
        """Devuelve la conversación activa para un usuario, o None si no hay."""
        return self.active.get(token)

    def set_active_conversation(self, token: str, conv_id: str):
        """Cambia la conversación activa de un usuario."""
        if token in self.conversations and conv_id in self.conversations[token]:
            self.active[token] = conv_id

    def add_message(self, conv_id: str, role: str, content: str, token: str | None = None):
        """Agrega un mensaje a una conversación concreta."""
        if token:
            convs = self.conversations.setdefault(token, {})
            convs.setdefault(conv_id, []).append({"role": role, "content": content})
        else:
            # si no hay token, buscar en cualquier usuario
            for convs in self.conversations.values():
                if conv_id in convs:
                    convs[conv_id].append({"role": role, "content": content})
                    break

    def get_conversation(self, conv_id: str, token: str | None = None) -> list[dict]:
        """Devuelve el historial de una conversación."""
        if token:
            return self.conversations.get(token, {}).get(conv_id, [])
        for convs in self.conversations.values():
            if conv_id in convs:
                return convs[conv_id]
        return []

    def respond(self, conv_id: str, user_message: str, token: str | None = None) -> str:
        """
        Genera una respuesta simulada del bot.
        Aquí puedes conectar con tu modelo real (OpenAI, etc.).
        """
        # De momento una respuesta placeholder
        return f"Recibido: {user_message}"

# ✅ instancia global que usa bot.py
memory = Memory()
