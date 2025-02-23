import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime, timedelta
import pickle
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ImprovedNewsRecommender:
    def __init__(self):
        self.news_df = None
        self.user_df = None
        self.tfidf_matrix = None
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.popularity_scores = None

    def load_and_prepare_data(self, data_dir: str) -> None:
        """Carrega e prepara os dados."""
        from app.data_loader import DataLoader
        logger.info("Carregando dados...")
        self.news_df, self.user_df = DataLoader.load_data(data_dir)
        
        # Adiciona timestamp às notícias
        self.news_df['timestamp'] = pd.to_datetime(self.news_df['date'])
        
        # Prepara conteúdo para TF-IDF
        logger.info("Preparando conteúdo para análise...")
        self.news_df['content'] = self.news_df.apply(
            lambda x: f"{x['title']} {x['body']} {x.get('caption', '')}", 
            axis=1
        )
        
        # Calcula TF-IDF
        logger.info("Calculando TF-IDF...")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.news_df['content'])
        
        # Calcula scores de popularidade com decay temporal
        logger.info("Calculando scores de popularidade...")
        self.calculate_popularity_scores()
        
        logger.info("Dados preparados com sucesso!")

    def calculate_time_decay(self, date) -> float:
        """Calcula o decay temporal para uma data."""
        now = datetime.now()
        age_in_days = (now - pd.to_datetime(date)).days
        decay = 1 / (1 + 0.1 * age_in_days)  # Decay exponencial simples
        return max(0.1, decay)  # Mantém um mínimo de 0.1 para notícias antigas

    def calculate_popularity_scores(self) -> None:
        """Calcula scores de popularidade das notícias com decay temporal."""
        all_histories = self.user_df['history'].str.split(',').explode()
        all_histories = all_histories.str.strip()
        view_counts = all_histories.value_counts()
        
        # Aplica decay temporal
        self.popularity_scores = pd.Series(index=view_counts.index, dtype=float)
        for article_id in view_counts.index:
            article_date = self.news_df[self.news_df['Page'] == article_id]['timestamp'].iloc[0]
            decay = self.calculate_time_decay(article_date)
            self.popularity_scores[article_id] = view_counts[article_id] * decay

        # Normaliza os scores
        self.popularity_scores = self.popularity_scores / self.popularity_scores.max()

    def get_recommendations_for_new_user(self, n: int = 5) -> List[dict]:
        """Recomendações para usuários novos (cold-start)."""
        # Combina notícias populares recentes com algumas mais antigas mas muito populares
        recent_mask = (datetime.now() - self.news_df['timestamp']) <= timedelta(days=2)
        recent_popular = self.news_df[recent_mask].nlargest(n//2, 'popularity_score')
        all_time_popular = self.news_df.nlargest(n//2, 'popularity_score')
        
        recommendations = pd.concat([recent_popular, all_time_popular]).drop_duplicates()
        
        return [
            {
                'article_id': row['Page'],
                'title': row['title'],
                'url': row['url'],
                'score': self.popularity_scores.get(row['Page'], 0)
            }
            for _, row in recommendations.iterrows()
        ][:n]

    def get_user_recommendations(self, user_id: str, n: int = 5) -> List[dict]:
        """Retorna recomendações personalizadas para um usuário."""
        try:
            user_data = self.user_df[self.user_df['userId'] == user_id].iloc[0]
            
            # Para usuários sem histórico, retorna as mais populares
            if user_data['historySize'] == 0:
                return self.get_recommendations_for_new_user(n)
            
            # Obtém últimos artigos lidos
            history = [x.strip() for x in user_data['history'].split(',')]
            last_article = history[-1]
            
            # Gera recomendações baseadas no último artigo lido
            content_recs = self.get_content_based_recommendations(last_article, n)
            
            # Obtém recomendações populares
            popular_recs = self.get_popular_recommendations(n)
            
            # Mescla recomendações
            all_recs = []
            used_articles = set(history)
            
            # Define peso simples baseado no tamanho do histórico
            content_weight = 0.7 if user_data['historySize'] > 5 else 0.3
            
            for article in (content_recs + popular_recs):
                if article['article_id'] not in used_articles and len(all_recs) < n:
                    # Aplica decay temporal
                    article_date = self.news_df[
                        self.news_df['Page'] == article['article_id']
                    ]['timestamp'].iloc[0]
                    time_decay = self.calculate_time_decay(article_date)
                    
                    # Calcula score final
                    if article in content_recs:
                        article['score'] *= content_weight * time_decay
                    else:
                        article['score'] *= (1 - content_weight) * time_decay
                    
                    all_recs.append(article)
                    used_articles.add(article['article_id'])
            
            # Ordena por score final
            return sorted(all_recs, key=lambda x: x['score'], reverse=True)[:n]
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações para usuário: {str(e)}")
            return self.get_recommendations_for_new_user(n)

    def get_content_based_recommendations(self, article_id: str, n: int = 5) -> List[dict]:
        """Retorna recomendações baseadas em conteúdo similar."""
        try:
            article_idx = self.news_df[self.news_df['Page'] == article_id].index[0]
            article_vector = self.tfidf_matrix[article_idx]
            
            similarities = cosine_similarity(article_vector, self.tfidf_matrix)
            similar_indices = similarities.argsort()[0][-n-1:-1][::-1]
            
            recommendations = []
            for idx in similar_indices:
                article_data = self.news_df.iloc[idx]
                recommendations.append({
                    'article_id': article_data['Page'],
                    'title': article_data['title'],
                    'url': article_data['url'],
                    'score': float(similarities[0][idx])
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações por conteúdo: {str(e)}")
            return []

    def get_popular_recommendations(self, n: int = 5) -> List[dict]:
        """Retorna as notícias mais populares."""
        try:
            top_articles = self.popularity_scores.nlargest(n).index
            recommendations = []
            
            for article_id in top_articles:
                article_data = self.news_df[self.news_df['Page'] == article_id].iloc[0]
                recommendations.append({
                    'article_id': article_id,
                    'title': article_data['title'],
                    'url': article_data['url'],
                    'score': float(self.popularity_scores[article_id])
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Erro ao obter recomendações populares: {str(e)}")
            return []

    def save_model(self, path: str) -> None:
        """Salva o modelo."""
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load_model(cls, path: str) -> 'ImprovedNewsRecommender':
        """Carrega um modelo salvo."""
        with open(path, 'rb') as f:
            return pickle.load(f)