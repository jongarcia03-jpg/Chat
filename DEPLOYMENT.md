# Despliegue en Google Cloud

## Variables de entorno
- `OPENROUTER_API_KEY`: cargar desde Secret Manager en Cloud Run. En local se lee desde `backend/.env` (copiar de `.env.example`).
- `DATABASE_URL`:
  - Desarrollo local: `sqlite:///./chatbot.db` (valor por defecto).
  - Produccion: URL de Cloud SQL Postgres, por ejemplo `postgresql+psycopg://USER:PASSWORD@/DATABASE?host=/cloudsql/INSTANCE`.
- `OPENROUTER_MODEL`: opcional, modelo usado por OpenRouter.

## Backend
1. Habilita APIs `run`, `cloudbuild`, `artifactregistry`, `secretmanager`, `sqladmin`.
2. Construye y publica la imagen:
   ```bash
   gcloud builds submit --config=cloudbuild-backend.yaml .
   ```
3. Despliega en Cloud Run:
   ```bash
   gcloud run deploy chat-backend \
     --image=us-central1-docker.pkg.dev/PROJECT/chat-repo/backend:1 \
     --region=us-central1 \
     --platform=managed \
     --set-env-vars="DATABASE_URL=postgresql+psycopg://..." \
     --update-secrets="OPENROUTER_API_KEY=openrouter-api-key:latest" \
     --add-cloudsql-instances=PROJECT:REGION:INSTANCE
   ```
4. Define la variable `OPENROUTER_API_KEY` mediante Secret Manager.

## Frontend
- Configura `VITE_API_URL` apuntando a la URL de Cloud Run del backend.
- Puedes construir y servir con Cloud Run (`frontend/Dockerfile`) o subir `frontend/dist` a Cloud Storage + Cloud CDN.

## Funcionamiento local
- `docker-compose up --build` sigue funcionando con SQLite.
- Crea `backend/.env` a partir de `.env.example` con tu clave real.
- `frontend/.env` debe apuntar a `http://localhost:8000`.
