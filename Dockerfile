FROM python:3-alpine

# Instalar dependências do sistema
RUN apk add --no-cache \
    build-base \
    curl

# Criar e mudar para o diretório da aplicação
WORKDIR /app

# Copiar todo o código local para o container
COPY . .

# Criar diretórios necessários
RUN mkdir -p data/raw models

# Instalar dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Configurar variáveis de ambiente
ENV MODEL_DIR=/app/models
ENV DATA_DIR=/app/data/raw

# Expor porta
EXPOSE 8000

# Executar o serviço web na inicialização do container
CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:$PORT"]