FROM python:3.9-slim

# Configura variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MODEL_DIR=/app/models
ENV GCS_BUCKET_NAME=news-recommender-models
ENV GCS_BLOB_NAME=recommender.pkl
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação e as credenciais
COPY app/ app/
COPY Procfile .
COPY credentials.json .

# Comando para executar a aplicação
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT