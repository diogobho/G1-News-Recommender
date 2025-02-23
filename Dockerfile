FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app/ app/

# Criar diretórios necessários
RUN mkdir -p data/raw models

# Configurar usuário não-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Configurar variáveis de ambiente
ENV PORT=8000
ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data/raw

# Expor porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]