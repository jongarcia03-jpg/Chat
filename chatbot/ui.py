import gradio as gr
from chatbot.bot import get_response
from chatbot.memory import ChatMemory
from chatbot.persistence import save_conversations, load_conversations
from chatbot.tts import text_to_speech
from chatbot.utils import generate_title
import uuid
from datetime import datetime

# ==============================
#   Estado global
# ==============================
conversations = load_conversations()
current_conversation = list(conversations.keys())[-1] if conversations else None

# ==============================
#   Funciones de conversación
# ==============================
def new_conversation():
    global current_conversation
    conv_id = str(uuid.uuid4())[:8]
    title = f"Chat {datetime.now().strftime('%d/%m %H:%M')}"
    conversations[conv_id] = {"title": title, "memory": ChatMemory()}
    current_conversation = conv_id
    save_conversations(conversations)
    return "", [], gr.update(choices=[c["title"] for c in conversations.values()], value=title)

def select_conversation(selected_title):
    global current_conversation
    for cid, conv in conversations.items():
        if conv["title"] == selected_title:
            current_conversation = cid
            return "", conv["memory"].get_history()
    return "", []

def chat(user_input):
    global current_conversation
    if current_conversation is None:
        new_conversation()
    memory = conversations[current_conversation]["memory"]

    memory.add_message("user", user_input)
    response = get_response(user_input, history=memory.get_history())

    if not response or not response.strip():
        response = "Lo siento, no tengo respuesta para eso."

    memory.add_message("assistant", response)

    if len(memory.get_history()) <= 2:
        conversations[current_conversation]["title"] = generate_title(user_input)

    save_conversations(conversations)
    return "", memory.get_history(), gr.update(
        choices=[c["title"] for c in conversations.values()],
        value=conversations[current_conversation]["title"]
    )

def text_to_speech_last():
    global current_conversation
    if current_conversation is None:
        return None
    memory = conversations[current_conversation]["memory"]
    assistant_messages = [m for m in memory.get_history() if m["role"] == "assistant"]
    if not assistant_messages:
        return None
    return text_to_speech(assistant_messages[-1]["content"])

def stop_speech():
    """Detener la reproducción de voz"""
    return None

# ==============================
#   Construcción de la UI
# ==============================
def build_ui():
    initial_titles = [c["title"] for c in conversations.values()]
    initial_value = conversations[current_conversation]["title"] if current_conversation else None
    initial_history = conversations[current_conversation]["memory"].get_history() if current_conversation else []

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
/* Ocultar labels */
.label-wrap {
    display: none !important;
}
""") as demo:
        gr.Markdown("# 🤖 Chatbot modular con historial persistente (gTTS)")

        with gr.Row():
            with gr.Column(scale=2):
                conv_list = gr.Dropdown(
                    label="Conversaciones",
                    choices=initial_titles,
                    value=initial_value,
                    interactive=True
                )
                new_conv_btn = gr.Button("➕ Nueva conversación")
            with gr.Column(scale=8):
                chatbot_ui = gr.Chatbot(type="messages", value=initial_history)
                with gr.Row():
                    msg = gr.Textbox(placeholder="Escribe tu mensaje...", scale=9)
                    speak_btn = gr.Button("🔊", elem_classes="speak-btn", scale=1)
                    stop_btn = gr.Button("⏹️", elem_classes="speak-btn", scale=1)
                audio_out = gr.Audio(type="filepath", autoplay=True, elem_classes="hidden-audio")

        # Eventos
        new_conv_btn.click(new_conversation, outputs=[msg, chatbot_ui, conv_list])
        conv_list.change(select_conversation, conv_list, [msg, chatbot_ui])
        msg.submit(chat, msg, [msg, chatbot_ui, conv_list])
        speak_btn.click(text_to_speech_last, inputs=[], outputs=audio_out)
        stop_btn.click(stop_speech, inputs=[], outputs=audio_out)

    return demo
