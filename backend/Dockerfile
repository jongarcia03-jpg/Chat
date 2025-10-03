# Imagen base ligera con Python
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias necesarias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt desde backend
COPY ./backend/requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el backend al contenedor
COPY ./backend .

# Exponer puerto de FastAPI
EXPOSE 8000

# Ejecutar la aplicación
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
