import pyttsx3
import gradio as gr
from chatbot.bot import get_response
from chatbot.memory import ChatMemory
import tempfile

# Inicializar memoria y motor TTS
memory = ChatMemory()
engine = pyttsx3.init()

def chat(user_input):
    """Procesa el mensaje del usuario y devuelve la respuesta del bot"""
    memory.add_message("user", user_input)
    response = get_response(user_input, history=memory.get_history())
    memory.add_message("assistant", response)
    return response

def submit_fn(user_input):
    """Enviar mensaje y actualizar chat"""
    response = chat(user_input)
    messages = memory.get_history()
    return "", messages, None

def text_to_speech_last():
    """Lee en voz alta el último mensaje del bot"""
    assistant_messages = [m for m in memory.get_history() if m["role"] == "assistant"]
    if not assistant_messages:
        return None
    text = assistant_messages[-1]["content"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name

    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

with gr.Blocks(css="""
.speak-btn button {
    min-width: 40px;
    max-width: 40px;
    height: 40px;
    font-size: 20px;
}
.hidden-audio {
    height: 1px !important;
    visibility: hidden;
}
""") as demo:
    gr.Markdown("# 🤖 Chatbot con OpenRouter + Voz")

    chatbot_ui = gr.Chatbot(type="messages")
    
    with gr.Row():
        msg = gr.Textbox(placeholder="Escribe tu mensaje...", scale=9)
        speak_btn = gr.Button("🔊", elem_classes="speak-btn", scale=1)

    # 🔊 El audio existe pero está oculto con CSS
    audio_out = gr.Audio(type="filepath", autoplay=True, elem_classes="hidden-audio")

    # Enviar mensaje
    msg.submit(submit_fn, msg, [msg, chatbot_ui, audio_out])

    # Leer en alto último mensaje del bot
    speak_btn.click(
        text_to_speech_last,
        inputs=[],
        outputs=audio_out
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
