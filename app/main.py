from fastapi import FastAPI, HTTPException
from typing import List, Optional
from app.recommender import ImprovedNewsRecommender
from app.storage_service import StorageService  # Novo serviço
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

# Configurações do Cloud Storage
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "news-recommender-models")  # Substitua pelo nome do seu bucket
BLOB_NAME = os.getenv("GCS_BLOB_NAME", "recommender.pkl")


# Garante que o diretório models existe
Path(MODEL_DIR).mkdir(parents=True, exist_ok=True)

# Caminho do modelo local (fallback)
model_path = os.path.join(MODEL_DIR, "recommender.pkl")
recommender = None

@app.on_event("startup")
async def startup_event():
    """Carrega o modelo do Google Cloud Storage na inicialização."""
    global recommender
    
    try:
        logger.info(f"Tentando carregar modelo do Cloud Storage: {BUCKET_NAME}/{BLOB_NAME}")
        recommender = StorageService.load_model_from_storage(BUCKET_NAME, BLOB_NAME)
        
        if recommender is not None:
            logger.info("Modelo carregado com sucesso do Cloud Storage!")
        else:
            # Tenta carregar modelo local como fallback
            if os.path.exists(model_path):
                logger.info("Modelo do Storage falhou, tentando carregar modelo local...")
                recommender = ImprovedNewsRecommender.load_model(model_path)
                logger.info("Modelo local carregado com sucesso!")
            else:
                logger.warning("Nenhum modelo disponível. API funcionará em modo limitado.")
                recommender = ImprovedNewsRecommender()
    except Exception as e:
        logger.error(f"Erro ao inicializar o modelo: {str(e)}")
        logger.warning("API funcionará em modo limitado.")
        recommender = ImprovedNewsRecommender()

# Resto do código permanece o mesmo
# ...

@app.get("/reload-model")
async def reload_model():
    """Endpoint para recarregar o modelo do Google Cloud Storage."""
    global recommender
    
    try:
        logger.info(f"Recarregando modelo do Cloud Storage: {BUCKET_NAME}/{BLOB_NAME}")
        new_recommender = StorageService.load_model_from_storage(BUCKET_NAME, BLOB_NAME)
        
        if new_recommender is not None:
            recommender = new_recommender
            logger.info("Modelo recarregado com sucesso!")
            return {"status": "success", "message": "Modelo recarregado com sucesso"}
        else:
            return {"status": "error", "message": "Falha ao recarregar modelo"}
    except Exception as e:
        logger.error(f"Erro ao recarregar modelo: {str(e)}")
        return {"status": "error", "message": f"Erro ao recarregar modelo: {str(e)}"}
    
@app.get("/")
async def root():
    """Endpoint raiz com informações básicas."""
    return {
        "app": "G1 News Recommender",
        "status": "running",
        "model_status": "loaded_from_storage" if recommender else "limited",
        "endpoints": [
            "/recommend/{user_id}",
            "/popular",
            "/health",
            "/reload-model"
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
            "mode": "loaded_from_storage" if recommender else "limited"
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
            "mode": "loaded_from_storage" if recommender else "limited"
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
        "model_status": "loaded_from_storage" if recommender else "limited",
        "model_source": "google_cloud_storage"
    }