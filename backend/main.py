import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from chatbot.bot import get_response
from chatbot.tts import text_to_speech
from chatbot.utils import generate_title
from chatbot.models import init_db, SessionLocal, User, Conversation, Message
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
import uuid, tempfile, re

# ==============================
# Cargar variables de entorno
# ==============================
load_dotenv()

# ==============================
# Inicialización
# ==============================
app = FastAPI()
init_db()

# Carpeta temporal para audios
AUDIO_DIR = os.path.join(tempfile.gettempdir(), "chatbot_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Servir archivos estáticos en /audio
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sesiones en memoria: token -> user_id
sessions = {}

# ==============================
# Modelos de entrada
# ==============================
class ChatRequest(BaseModel):
    message: str

class SpeakRequest(BaseModel):
    text: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ==============================
# DB helper
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    if authorization not in sessions:
        raise HTTPException(status_code=401, detail="No autorizado")
    user_id = sessions[authorization]
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# ==============================
# Rutas de autenticación
# ==============================
@app.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    user = User(username=req.username, password_hash=bcrypt.hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"ok": True, "msg": "Usuario registrado"}

@app.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=req.username).first()
    if not user or not user.verify_password(req.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = str(uuid.uuid4())
    sessions[token] = user.id
    return {"token": token}

# ==============================
# Rutas de conversaciones
# ==============================
@app.get("/conversations")
def get_conversations(user: User = Depends(get_current_user)):
    return {conv.id: {"title": conv.title} for conv in user.conversations}

@app.get("/conversations/{cid}")
def get_conversation(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter_by(id=cid, user_id=user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="No existe la conversación")
    return {
        "id": conv.id,
        "title": conv.title,
        "history": [{"role": m.role, "content": m.content} for m in conv.messages]
    }

@app.post("/conversations")
def new_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = Conversation(user_id=user.id, title="Nueva conversación")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title}

@app.delete("/conversations/{cid}")
def delete_conversation(cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter_by(id=cid, user_id=user.id).first()
    if conv:
        db.delete(conv)
        db.commit()
    return {"ok": True}

# ==============================
# Chat y TTS
# ==============================
@app.post("/chat")
def chat(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = db.query(Conversation).filter_by(user_id=user.id).order_by(Conversation.id.desc()).first()
    if not conv:
        conv = Conversation(user_id=user.id, title="Nueva conversación")
        db.add(conv)
        db.commit()
        db.refresh(conv)

    # Guardar mensaje del usuario
    msg_user = Message(role="user", content=req.message, conversation_id=conv.id)
    db.add(msg_user)

    # Historial
    history = [{"role": m.role, "content": m.content} for m in conv.messages] + [{"role": "user", "content": req.message}]

    # Llamada a IA
    response_text = get_response(req.message, history=history) or "Lo siento, no tengo respuesta para eso."

    # Guardar respuesta
    msg_bot = Message(role="assistant", content=response_text, conversation_id=conv.id)
    db.add(msg_bot)

    # ✅ Generar título con IA solo en la primera interacción
    if conv.title == "Nueva conversación":
        conv.title = generate_title(req.message)
        db.commit()

    db.commit()

    return {"response": response_text, "history": history + [{"role": "assistant", "content": response_text}]}

def clean_text(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002700-\U000027BF"
        u"\U0001F900-\U0001F9FF"
        u"\U00002600-\U000026FF"
        u"\U00002B00-\U00002BFF"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)

@app.post("/speak")
async def speak(payload: dict):
    raw_text = payload.get("text", "")
    clean = clean_text(raw_text)
    filepath = text_to_speech(clean)
    filename = os.path.basename(filepath)
    return {"audio_url": f"http://localhost:8000/audio/{filename}"}
