class ChatMemory:
    def __init__(self, max_len=10):
        self.max_len = max_len
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_len:
            self.history.pop(0)

    def get_history(self):
        return self.history
