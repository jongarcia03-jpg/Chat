import re
from datetime import datetime

def clean_text(text: str) -> str:
    """Eliminar emojis y caracteres raros antes de pasarlos a gTTS"""
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

def generate_title(user_input):
    """Generar título con preview del primer mensaje"""
    short_preview = (user_input[:20] + "...") if len(user_input) > 20 else user_input
    return f"{short_preview} ({datetime.now().strftime('%d/%m %H:%M')})"
