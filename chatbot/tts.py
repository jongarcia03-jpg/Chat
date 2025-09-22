from gtts import gTTS
import tempfile
from chatbot.utils import clean_text

def text_to_speech(text):
    """Convierte texto en archivo de audio usando gTTS"""
    text = clean_text(text)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        filename = f.name
    gTTS(text=text, lang="es", slow=False).save(filename)
    return filename
