import gradio as gr
from gtts import gTTS
from chatbot.bot import get_response
from chatbot.memory import ChatMemory
import tempfile
import re
import uuid
import json
from datetime import datetime
import os

# ==============================
#   Manejo de conversaciones
# ==============================
SAVE_FILE = "conversations.json"
conversations = {}
current_conversation = None

def save_conversations():
    """Guardar conversaciones en JSON"""
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
    """Cargar conversaciones desde JSON"""
    global conversations, current_conversation
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
        # Seleccionar la última conversación guardada
        if conversations:
            current_conversation = list(conversations.keys())[-1]

load_conversations()

# ==============================
#   Funciones de conversación
# ==============================
def new_conversation():
    global current_conversation
    conv_id = str(uuid.uuid4())[:8]
    title = f"Chat {datetime.now().strftime('%d/%m %H:%M')}"
    conversations[conv_id] = {"title": title, "memory": ChatMemory()}
    current_conversation = conv_id
    save_conversations()
    titles = [c["title"] for c in conversations.values()]
    return "", [], gr.update(choices=titles, value=title)

def select_conversation(selected_title):
    global current_conversation
    for cid, conv in conversations.items():
        if conv["title"] == selected_title:
            current_conversation = cid
            messages = conv["memory"].get_history()
            return "", messages
    return "", []

# ==============================
#   Limpieza de texto para TTS
# ==============================
def clean_text(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002700-\U000027BF"
        "\U0001F900-\U0001F9FF"
        "\U00002600-\U000026FF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# ==============================
#   Funciones del chatbot
# ==============================
def chat(user_input):
    global current_conversation
    if current_conversation is None:
        new_conversation()
    memory = conversations[current_conversation]["memory"]

    memory.add_message("user", user_input)
    response = get_response(user_input, history=memory.get_history())

    # 🛠️ Evitar respuestas vacías
    if not response or not response.strip():
        response = "Lo siento, no tengo respuesta para eso."

    memory.add_message("assistant", response)

    # Actualizar título si es el primer mensaje
    if len(memory.get_history()) <= 2:
        short_preview = (user_input[:20] + "...") if len(user_input) > 20 else user_input
        conversations[current_conversation]["title"] = f"{short_preview} ({datetime.now().strftime('%d/%m %H:%M')})"

    save_conversations()
    titles = [c["title"] for c in conversations.values()]
    return "", memory.get_history(), gr.update(choices=titles, value=conversations[current_conversation]["title"])

def text_to_speech_last():
    global current_conversation
    if current_conversation is None:
        return None
    memory = conversations[current_conversation]["memory"]

    assistant_messages = [m for m in memory.get_history() if m["role"] == "assistant"]
    if not assistant_messages:
        return None
    text = clean_text(assistant_messages[-1]["content"])

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    gTTS(text=text, lang="es", slow=False).save(filename)
    return filename

# ==============================
#   Inicialización para la UI
# ==============================
initial_titles = [c["title"] for c in conversations.values()]
initial_value = None
initial_history = []

if conversations:
    # Mostrar última conversación
    last_cid = list(conversations.keys())[-1]
    initial_value = conversations[last_cid]["title"]
    initial_history = conversations[last_cid]["memory"].get_history()

# ==============================
#   Interfaz con Gradio
# ==============================
with gr.Blocks(css="""
/* Botón de voz */
.speak-btn button {
    min-width: 40px;
    max-width: 40px;
    height: 40px;
    font-size: 20px;
}
/* Ocultar reproductor de audio */
.hidden-audio {
    height: 1px !important;
    visibility: hidden;
}
/* Ocultar texto 'processing' */
.wrap.svelte-1ipelgc {
    display: none !important;
}
/* Ocultar labels de componentes */
.label-wrap {
    display: none !important;
}
""") as demo:
    gr.Markdown("# 🤖 Chatbot con historial persistente (gTTS)")

    with gr.Row():
        with gr.Column(scale=2):  # Sidebar izquierda
            conv_list = gr.Dropdown(
                label="Conversaciones",
                choices=initial_titles,
                value=initial_value,
                interactive=True
            )
            new_conv_btn = gr.Button("➕ Nueva conversación")
        with gr.Column(scale=8):  # Chat derecha
            chatbot_ui = gr.Chatbot(type="messages", value=initial_history)
            with gr.Row():
                msg = gr.Textbox(placeholder="Escribe tu mensaje...", scale=9)
                speak_btn = gr.Button("🔊", elem_classes="speak-btn", scale=1)
            audio_out = gr.Audio(type="filepath", autoplay=True, elem_classes="hidden-audio")

    # Nueva conversación
    new_conv_btn.click(new_conversation, outputs=[msg, chatbot_ui, conv_list])

    # Seleccionar conversación
    conv_list.change(select_conversation, conv_list, [msg, chatbot_ui])

    # Enviar mensaje
    msg.submit(chat, msg, [msg, chatbot_ui, conv_list])

    # Leer último mensaje
    speak_btn.click(text_to_speech_last, inputs=[], outputs=audio_out)

demo.launch(server_name="0.0.0.0", server_port=7860)
