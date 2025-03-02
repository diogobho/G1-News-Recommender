# G1 News Recommender

Sistema de recomendação de notícias para a plataforma G1, utilizando técnicas de filtragem baseada em conteúdo e popularidade, com acesso a modelos via Google Cloud Storage.

## Índice

- [Visão Geral](#visão-geral)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Detalhes da Implementação](#detalhes-da-implementação)
  - [Sistema de Recomendação](#sistema-de-recomendação)
  - [Acesso ao Modelo via Google Cloud Storage](#acesso-ao-modelo-via-google-cloud-storage)
  - [API REST](#api-rest)
- [Configuração e Execução](#configuração-e-execução)
  - [Pré-requisitos](#pré-requisitos)
  - [Instalação](#instalação)
  - [Configuração do Google Cloud Storage](#configuração-do-google-cloud-storage)
  - [Execução](#execução)
- [Endpoints da API](#endpoints-da-api)
- [Implantação com Docker](#implantação-com-docker)
- [Desenvolvimento e Melhorias Futuras](#desenvolvimento-e-melhorias-futuras)

## Visão Geral

O G1 News Recommender é um sistema para recomendar notícias aos usuários da plataforma G1, baseado em seu histórico de leitura e na popularidade dos artigos. O sistema combina diferentes estratégias de recomendação para oferecer conteúdo relevante e diversificado aos usuários.

A aplicação é dividida em componentes principais:
- **Sistema de Recomendação**: Implementa técnicas de filtragem baseada em conteúdo e popularidade
- **Acesso ao Modelo**: Carrega o modelo pré-treinado diretamente do Google Cloud Storage para a memória
- **API REST**: Fornece endpoints para obter recomendações e informações do sistema

## Estrutura do Projeto

```
news_recommender/
│
├── app/
│   ├── __init__.py
│   ├── main.py               # Aplicação FastAPI e endpoints
│   ├── recommender.py        # Sistema de recomendação
│   ├── data_loader.py        # Carregamento e processamento de dados
│   └── storage_service.py    # Acesso ao Google Cloud Storage
│
├── models/                   # Diretório para o modelo local (fallback)
│   └── recommender.pkl       # Opcional - usado apenas como fallback
│
├── credentials.json          # Credenciais da conta de serviço Google Cloud
├── Dockerfile                # Configuração para containerização
├── requirements.txt          # Dependências do projeto
├── Procfile                  # Configuração para deploy em plataformas como Heroku
├── runtime.txt               # Versão do Python para ambientes de deploy
└── .gitignore                # Arquivos a serem ignorados pelo Git
```

## Detalhes da Implementação

### Sistema de Recomendação

O recomendador implementa uma abordagem híbrida que combina várias técnicas:

#### 1. Filtragem Baseada em Conteúdo

- **Processamento de Texto**: Utiliza TF-IDF (Term Frequency-Inverse Document Frequency) para transformar o conteúdo textual das notícias em vetores numéricos.
- **Similaridade de Cosseno**: Calcula a similaridade entre notícias usando o método de cosseno entre os vetores TF-IDF.
- **Recomendações Personalizadas**: Recomenda artigos similares aos últimos lidos pelo usuário.

#### 2. Filtragem por Popularidade

- **Contagem de Visualizações**: Rastreia a popularidade dos artigos com base no número de visualizações.
- **Decay Temporal**: Aplica um decay exponencial baseado na idade do artigo, favorecendo conteúdo mais recente.
- **Recomendações para Cold-Start**: Fornece recomendações populares para novos usuários sem histórico.

#### 3. Estratégias Híbridas

- **Balanceamento Adaptativo**: Ajusta o peso entre recomendações baseadas em conteúdo e popularidade dependendo do histórico do usuário.
- **Diversidade de Conteúdo**: Evita recomendar artigos já vistos pelo usuário.
- **Relevância Temporal**: Prioriza notícias recentes, mas ainda mantém artigos populares mais antigos.

### Acesso ao Modelo via Google Cloud Storage

O sistema acessa o modelo pré-treinado (recommender.pkl) diretamente do Google Cloud Storage, sem necessidade de download ou armazenamento local:

1. **Acesso via Conta de Serviço**: Utiliza uma conta de serviço do Google Cloud com permissões adequadas.
2. **Carregamento em Memória**: Carrega o modelo diretamente na memória RAM sem armazenamento intermediário em disco.
3. **Estratégia de Fallback**: Em caso de falha no acesso ao Cloud Storage, tenta usar um modelo local se disponível.
4. **Recarregamento sob Demanda**: Oferece um endpoint para recarregar o modelo sem reiniciar a aplicação.

### API REST

A API foi desenvolvida utilizando FastAPI, oferecendo:

- **Documentação Automática**: Documentação interativa via Swagger UI (/docs) e ReDoc (/redoc).
- **Endpoints RESTful**: Interfaces claras para obter recomendações e informações do sistema.
- **Tratamento de Exceções**: Gestão adequada de erros com feedback informativo.
- **Logging Abrangente**: Registro detalhado de operações, facilitando monitoramento e debugging.

## Configuração e Execução

### Pré-requisitos

- Python 3.9 ou superior
- Conta no Google Cloud com acesso ao Cloud Storage
- Credenciais de uma conta de serviço com permissões para o Cloud Storage

### Instalação

1. Clone o repositório:
```bash
git clone <repositório>
cd news_recommender
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Configuração do Google Cloud Storage

1. Crie um bucket no Google Cloud Storage (ex: "news-recommender-models").

2. Faça upload do seu modelo treinado (recommender.pkl) para o bucket.

3. Crie uma conta de serviço com permissões para acessar o bucket (papel "Storage Object Viewer" ou similar).

4. Baixe o arquivo JSON com as credenciais da conta de serviço e salve-o como `credentials.json` na raiz do projeto.

5. Certifique-se de que o arquivo credentials.json não seja versionado (inclua-o no .gitignore).

### Execução

Execute a aplicação localmente:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a API em `http://localhost:8000` e a documentação em `http://localhost:8000/docs`.

## Endpoints da API

- **GET /** - Informações básicas sobre a API
- **GET /health** - Verificação de saúde da API
- **GET /recommend/{user_id}** - Recomendações personalizadas para um usuário
  - Parâmetros: `n` (número de recomendações, padrão=5)
- **GET /popular** - Notícias mais populares
  - Parâmetros: `n` (número de notícias, padrão=5)
- **GET /reload-model** - Recarrega o modelo do Cloud Storage

## Implantação com Docker

1. Construa a imagem Docker:
```bash
docker build -t news-recommender .
```

2. Execute o contêiner:
```bash
docker run -p 8000:8000 news-recommender
```

Para implantação em ambientes de produção, considere ajustar as configurações do Dockerfile e utilizar um orquestrador como Kubernetes.

## Desenvolvimento e Melhorias Futuras

### Possíveis Melhorias

1. **Avaliação e Métricas**:
   - Implementar avaliação offline usando métricas como precisão, recall e NDCG
   - Adicionar testes A/B para avaliar o impacto das recomendações

2. **Estratégias Adicionais**:
   - Filtragem colaborativa para identificar padrões entre usuários similares
   - Incorporação de feedback explícito dos usuários
   - Análise de sentimento para conteúdo de notícias

3. **Escalabilidade**:
   - Implementação de cache distribuído
   - Processamento assíncrono para recomendações
   - Uso de filas de mensagens para processamento em lote

4. **Monitoramento**:
   - Implementação de métricas e dashboards
   - Alertas para falhas no sistema
   - Rastreamento de desempenho das recomendações

### Manutenção do Modelo

Para atualizar o modelo:

1. Treine um novo modelo com dados atualizados
2. Faça upload do novo modelo para o Cloud Storage (mantendo o mesmo nome)
3. Acesse o endpoint `/reload-model` para carregar a nova versão

---

Para mais informações, consulte a documentação interativa da API ou entre em contato com a equipe de desenvolvimento.
