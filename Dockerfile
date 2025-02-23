FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar e mudar para o diretório da aplicação
WORKDIR /app

# Copiar requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o resto do código
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/raw models

# Configurar variáveis de ambiente
ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data/raw

# Expor porta
EXPOSE 8000

# Executar o serviço web
CMD hypercorn app.main:app --bind 0.0.0.0:$PORT