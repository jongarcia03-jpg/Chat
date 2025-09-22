from openai import OpenAI
from config import OPENROUTER_API_KEY, MODEL_NAME

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

def get_response(prompt, history=None):
    messages = []

    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": prompt})

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=0.7,
        max_tokens=5000,
        extra_headers={},
        extra_body={}
    )

    text = completion.choices[0].message.content
    return text
