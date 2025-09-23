def generate_title(prompt: str) -> str:
    words = prompt.split()
    return " ".join(words[:3]) + ("..." if len(words) > 3 else "")
