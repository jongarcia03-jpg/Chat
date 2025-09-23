from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chatbot.memory import ChatMemory
from chatbot.bot import get_response
from chatbot.tts import text_to_speech
from chatbot.persistence import save_conversations, load_conversations
from chatbot.utils import generate_title
import uuid, os, tempfile

# ==============================
# Inicialización
# ==============================
app = FastAPI()
conversations = load_conversations()
current_conversation = list(conversations.keys())[-1] if conversations else None

# Carpeta temporal para audios
AUDIO_DIR = os.path.join(tempfile.gettempdir(), "chatbot_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Servir archivos estáticos en /audio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# CORS para React u otros clientes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Modelos
# ==============================
class ChatRequest(BaseModel):
    message: str

class SpeakRequest(BaseModel):
    text: str

# ==============================
# Rutas
# ==============================
@app.post("/chat")
async def chat(req: ChatRequest):
    global current_conversation

    if current_conversation is None:
        conv_id = str(uuid.uuid4())[:8]
        conversations[conv_id] = {"title": "Nueva conversación", "memory": ChatMemory()}
        current_conversation = conv_id

    memory = conversations[current_conversation]["memory"]

    memory.add_message("user", req.message)
    response = get_response(req.message, history=memory.get_history())
    if not response or not response.strip():
        response = "Lo siento, no tengo respuesta para eso."
    memory.add_message("assistant", response)

    if len(memory.get_history()) <= 2:
        conversations[current_conversation]["title"] = generate_title(req.message)

    save_conversations(conversations)

    return {"response": response, "history": memory.get_history()}

@app.post("/speak")
async def speak(req: SpeakRequest):
    path = text_to_speech(req.text)
    filename = os.path.basename(path)

    # 👉 Devuelve la URL accesible desde Docker (usando el servicio "backend")
    return {"audio_url": f"http://backend:8000/audio/{filename}"}

@app.get("/conversations")
async def get_conversations():
    return {cid: {"title": conv["title"]} for cid, conv in conversations.items()}

@app.get("/conversations/{cid}")
async def get_conversation(cid: str):
    if cid not in conversations:
        return {"error": "No existe la conversación"}
    return {"id": cid, "title": conversations[cid]["title"], "history": conversations[cid]["memory"].get_history()}

@app.post("/conversations")
async def new_conversation():
    global current_conversation
    conv_id = str(uuid.uuid4())[:8]
    conversations[conv_id] = {"title": "Nueva conversación", "memory": ChatMemory()}
    current_conversation = conv_id
    save_conversations(conversations)
    return {"id": conv_id, "title": conversations[conv_id]["title"]}

@app.delete("/conversations/{cid}")
async def delete_conversation(cid: str):
    global current_conversation
    if cid in conversations:
        del conversations[cid]
        if current_conversation == cid:
            current_conversation = list(conversations.keys())[-1] if conversations else None
        save_conversations(conversations)
    return {"ok": True}
