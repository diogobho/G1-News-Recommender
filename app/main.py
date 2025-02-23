from fastapi import FastAPI, HTTPException
from typing import List, Optional
from app.recommender import ImprovedNewsRecommender
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cria a aplicação FastAPI
app = FastAPI(title="G1 News Recommender")

# Carrega o modelo
model_path = "models/recommender.pkl"
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
            logger.info("Modelo não encontrado. Treinando novo modelo...")
            recommender = ImprovedNewsRecommender()
            recommender.load_and_prepare_data("data/raw")
            
            # Criar diretório models se não existir
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Salvar o novo modelo
            recommender.save_model(model_path)
            logger.info("Novo modelo treinado e salvo com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao inicializar o modelo: {str(e)}")
        logger.info("Tentando treinar novo modelo...")
        try:
            recommender = ImprovedNewsRecommender()
            recommender.load_and_prepare_data("data/raw")
            recommender.save_model(model_path)
            logger.info("Novo modelo treinado e salvo com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao treinar novo modelo: {str(e)}")
            raise

@app.get("/recommend/{user_id}")
async def get_recommendations(user_id: str, n: Optional[int] = 5):
    """Endpoint para recomendações personalizadas."""
    if not recommender:
        raise HTTPException(status_code=500, detail="Modelo não carregado")
    
    recommendations = recommender.get_user_recommendations(user_id, n)
    return {
        "user_id": user_id,
        "recommendations": recommendations
    }

@app.get("/popular")
async def get_popular_news(n: Optional[int] = 5):
    """Endpoint para notícias populares."""
    if not recommender:
        raise HTTPException(status_code=500, detail="Modelo não carregado")
    
    return {
        "popular_news": recommender.get_popular_recommendations(n)
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da API."""
    return {
        "status": "healthy",
        "model_loaded": recommender is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)