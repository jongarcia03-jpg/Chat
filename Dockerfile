# Imagen base con Python
FROM python:3.11-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema para pyttsx3 y audio
RUN apt-get update && apt-get install -y \
    espeak ffmpeg libespeak-ng1 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Puerto para Gradio
EXPOSE 7860

# Comando de ejecución
CMD ["python", "app.py"]
