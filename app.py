import gradio as gr
from gtts import gTTS
from chatbot.bot import get_response
from chatbot.memory import ChatMemory
import tempfile
import re

# ==============================
#   Inicializar memoria
# ==============================
memory = ChatMemory()

# ==============================
#   Función para limpiar texto
# ==============================
def clean_text(text: str) -> str:
    """Elimina emojis y caracteres no soportados por gTTS"""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticonos
        "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        "\U0001F680-\U0001F6FF"  # transporte y mapas
        "\U0001F1E0-\U0001F1FF"  # banderas
        "\U00002700-\U000027BF"  # otros símbolos
        "\U0001F900-\U0001F9FF"  # símbolos suplementarios
        "\U00002600-\U000026FF"  # varios símbolos
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

# ==============================
#   Funciones del chatbot
# ==============================
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
    """Lee en voz alta el último mensaje del bot con gTTS en español neutro, sin emojis"""
    assistant_messages = [m for m in memory.get_history() if m["role"] == "assistant"]
    if not assistant_messages:
        return None
    text = assistant_messages[-1]["content"]

    # 🧹 limpiar texto antes de pasarlo a gTTS
    text = clean_text(text)

    # Crear archivo temporal único para cada audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    tts = gTTS(text=text, lang="es", slow=False)  # español neutro
    tts.save(filename)
    return filename

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
/* Ocultar el reproductor de audio */
.hidden-audio {
    height: 1px !important;
    visibility: hidden;
}
/* Ocultar texto de 'processing' */
.wrap.svelte-1ipelgc {
    display: none !important;
}
/* Ocultar títulos/labels de Chatbot y Textbox */
.label-wrap {
    display: none !important;
}
""") as demo:
    gr.Markdown("# 🤖 Chatbot con OpenRouter + Voz (gTTS)")

    chatbot_ui = gr.Chatbot(type="messages")  # sin label

    with gr.Row():
        msg = gr.Textbox(placeholder="Escribe tu mensaje...", scale=9)  # sin label
        speak_btn = gr.Button("🔊", elem_classes="speak-btn", scale=1)

    # 🔊 El audio se reproduce automáticamente pero está oculto
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
