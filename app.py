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
    messages = memory.get_history()  # lista de dicts {'role':..., 'content':...}
    return "", messages, None

def text_to_speech_last():
    """Lee en voz alta el último mensaje del bot"""
    # Obtener último mensaje de assistant
    assistant_messages = [m for m in memory.get_history() if m["role"] == "assistant"]
    if not assistant_messages:
        return None
    text = assistant_messages[-1]["content"]

    # Crear archivo temporal de audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name

    engine.save_to_file(text, filename)
    engine.runAndWait()
    return filename

with gr.Blocks() as demo:
    gr.Markdown("# Chatbot con OpenRouter + Botón de Voz")

    chatbot_ui = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Escribe tu mensaje...")
    audio_out = gr.Audio(label="Escucha la respuesta", type="filepath")

    # Enviar mensaje
    msg.submit(submit_fn, msg, [msg, chatbot_ui, audio_out])

    # Botón para leer en alto último mensaje del bot
    gr.Button("Leer en alto").click(
        text_to_speech_last,
        inputs=[],
        outputs=audio_out
    )

demo.launch()
