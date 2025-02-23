import pandas as pd
import glob
import os
from typing import Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLoader:
    @staticmethod
    def load_data(data_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Carrega os dados de notícias e usuários.
        
        Args:
            data_dir: Diretório contendo os arquivos CSV
        
        Returns:
            Tuple contendo DataFrame de notícias e DataFrame de usuários
        """
        # Carrega arquivos de notícias
        news_files = sorted(glob.glob(os.path.join(data_dir, 'itens-parte*.csv')))
        if not news_files:
            raise FileNotFoundError(f"Nenhum arquivo de notícias encontrado em {data_dir}")
        
        logger.info(f"Encontrados {len(news_files)} arquivos de notícias")
        
        news_dfs = []
        for file in news_files:
            logger.info(f"Carregando arquivo: {file}")
            df = pd.read_csv(file)
            # Renomeia a coluna 'page' para 'Page'
            if 'page' in df.columns:
                df = df.rename(columns={'page': 'Page'})
            
            # Adiciona coluna de timestamp se não existir
            if 'date' not in df.columns:
                df['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elif not pd.api.types.is_datetime64_any_dtype(df['date']):
                df['date'] = pd.to_datetime(df['date'])
                
            news_dfs.append(df)
        
        news_df = pd.concat(news_dfs, ignore_index=True)
        news_df.drop_duplicates(subset=['Page'], inplace=True)
        logger.info(f"Total de notícias carregadas: {len(news_df)}")

        # Carrega arquivos de usuários
        user_files = sorted(glob.glob(os.path.join(data_dir, 'treino_parte*.csv')))
        if not user_files:
            raise FileNotFoundError(f"Nenhum arquivo de usuários encontrado em {data_dir}")
            
        logger.info(f"Encontrados {len(user_files)} arquivos de usuários")
        
        user_dfs = []
        for file in user_files:
            logger.info(f"Carregando arquivo: {file}")
            df = pd.read_csv(file)
            # Renomeia a coluna se necessário
            if 'userId' not in df.columns and 'userid' in df.columns:
                df = df.rename(columns={'userid': 'userId'})
            user_dfs.append(df)
                
        user_df = pd.concat(user_dfs, ignore_index=True)
        user_df.drop_duplicates(subset=['userId'], inplace=True)
        logger.info(f"Total de usuários carregados: {len(user_df)}")

        return news_df, user_df