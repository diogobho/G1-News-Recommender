import os
import pickle
import io
import logging
from google.oauth2 import service_account
from google.cloud import storage

logger = logging.getLogger(__name__)

class StorageService:
    """
    Serviço para interagir com o Google Cloud Storage usando uma conta de serviço.
    Carrega arquivos diretamente na memória sem criar arquivos temporários.
    """
    
    @staticmethod
    def get_client():
        """Obtém o cliente do Google Cloud Storage usando credenciais de conta de serviço."""
        try:
            # Caminho para o arquivo de credenciais da conta de serviço
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
            
            if not os.path.exists(credentials_path):
                logger.error(f"Arquivo de credenciais não encontrado: {credentials_path}")
                return None
                
            # Cria o cliente do Storage com as credenciais
            client = storage.Client.from_service_account_json(credentials_path)
            
            return client
            
        except Exception as e:
            logger.error(f"Erro ao criar cliente do Storage: {str(e)}")
            return None
    
    @staticmethod
    def load_model_from_storage(bucket_name, blob_name):
        """
        Carrega um modelo pickle diretamente do Google Cloud Storage para a memória.
        
        Args:
            bucket_name: Nome do bucket no Google Cloud Storage
            blob_name: Nome do arquivo/blob no bucket
            
        Returns:
            O modelo carregado ou None em caso de erro
        """
        try:
            logger.info(f"Acessando modelo no Storage: bucket={bucket_name}, blob={blob_name}")
            
            # Obtém o cliente do Storage
            client = StorageService.get_client()
            if not client:
                logger.error("Não foi possível criar o cliente do Storage")
                return None
                
            # Acessa o bucket
            bucket = client.bucket(bucket_name)
            
            # Acessa o blob (arquivo)
            blob = bucket.blob(blob_name)
            
            # Cria um buffer de memória para receber o conteúdo
            buffer = io.BytesIO()
            
            # Faz download do conteúdo para o buffer em memória
            logger.info("Carregando modelo para memória...")
            blob.download_to_file(buffer)
            
            # Retorna o cursor para o início do buffer
            buffer.seek(0)
            
            # Carrega o modelo diretamente do buffer de memória
            model = pickle.load(buffer)
            logger.info("Modelo carregado com sucesso para memória")
            
            return model
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelo do Storage: {str(e)}")
            return None