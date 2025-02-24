from fastapi import FastAPI, HTTPException
from typing import List, Optional
from app.recommender import ImprovedNewsRecommender
import os
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI
app = FastAPI(
    title="G1 News Recommender",
    description="API de recomendação de notícias do G1",
    version="1.0.0"
)

# Configurações
MODEL_DIR = os.getenv("MODEL_DIR", "models")
PORT = int(os.getenv("PORT", 8000))

# Garante que o diretório models existe
Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

# Caminho do modelo
model_path = os.path.join(MODEL_DIR, "recommender.pkl")
recommender = None

@app.on_event("startup")
async def startup_event():
    """Carrega ou treina o modelo na inicialização."""
    global recommender
    
    try:
        if os.path.exists(model_path):
            logger.info("Tentando carregar modelo existente...")
            recommender = ImprovedNewsRecommender.load_model(model_path)
            logger.info("Modelo carregado com sucesso!")
        else:
            logger.warning("Modelo não encontrado.")
            logger.warning("API funcionará em modo limitado.")
            recommender = ImprovedNewsRecommender()
    except Exception as e:
        logger.error(f"Erro ao inicializar o modelo: {str(e)}")
        logger.warning("API funcionará em modo limitado.")
        recommender = ImprovedNewsRecommender()

@app.get("/")
async def root():
    """Endpoint raiz com informações básicas."""
    return {
        "app": "G1 News Recommender",
        "status": "running",
        "model_status": "limited" if not os.path.exists(model_path) else "full",
        "endpoints": [
            "/recommend/{user_id}",
            "/popular",
            "/health"
        ]
    }

@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: str, n: Optional[int] = 5):
    """Endpoint para recomendações personalizadas."""
    if not recommender:
        raise HTTPException(status_code=503, detail="Serviço não disponível")
    
    try:
        recommendations = recommender.get_user_recommendations(user_id, n)
        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "mode": "limited" if not os.path.exists(model_path) else "full"
        }
    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {str(e)}")
        return {
            "user_id": user_id,
            "recommendations": [],
            "mode": "error",
            "message": "Erro ao gerar recomendações"
        }

@app.get("/popular")
async def get_popular_news(n: Optional[int] = 5):
    """Endpoint para notícias populares."""
    if not recommender:
        raise HTTPException(status_code=503, detail="Serviço não disponível")
    
    try:
        return {
            "popular_news": recommender.get_popular_recommendations(n),
            "mode": "limited" if not os.path.exists(model_path) else "full"
        }
    except Exception as e:
        logger.error(f"Erro ao obter notícias populares: {str(e)}")
        return {
            "popular_news": [],
            "mode": "error",
            "message": "Erro ao obter notícias populares"
        }

@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API."""
    return {
        "status": "healthy",
        "model_status": "limited" if not os.path.exists(model_path) else "full",
        "model_dir_exists": os.path.exists(MODEL_DIR)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)