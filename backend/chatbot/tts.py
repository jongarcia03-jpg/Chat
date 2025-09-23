from gtts import gTTS
import os, tempfile

# Carpeta temporal compartida con main.py
AUDIO_DIR = os.path.join(tempfile.gettempdir(), "chatbot_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

def text_to_speech(text: str) -> str:
    safe_text = text.replace("🤖", "")  # quitar emojis que gTTS no lee bien
    tts = gTTS(safe_text, lang="es", tld="com", slow=False)
    filename = next(tempfile._get_candidate_names()) + ".mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    tts.save(filepath)
    return filepath
