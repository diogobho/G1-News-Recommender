FROM python:3.9-slim

# Configura variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MODEL_DIR=/app/models

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de requisitos primeiro
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o modelo e o código
COPY models/recommender.pkl models/
COPY app/ app/
COPY Procfile .

# Comando para executar a aplicação
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT