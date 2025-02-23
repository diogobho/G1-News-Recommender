# News Recommender System

Um sistema de recomendação de notícias baseado em conteúdo e popularidade, construído com FastAPI e scikit-learn.

## Visão Geral do Sistema

O sistema de recomendação combina duas abordagens principais:

1. **Recomendação Baseada em Conteúdo**: Utiliza TF-IDF e similaridade de cosseno para encontrar notícias similares baseadas no conteúdo textual (título, corpo e legenda).

2. **Recomendação por Popularidade**: Analisa o histórico de visualizações dos usuários para identificar as notícias mais populares.

### Como Funciona o Sistema de Recomendação

#### Processamento de Conteúdo
- O sistema utiliza TF-IDF (Term Frequency-Inverse Document Frequency) para converter o texto das notícias em vetores numéricos
- Combina título, corpo e legenda de cada notícia em um único texto para análise
- Limita-se a 5000 features mais relevantes para otimizar performance

#### Cálculo de Similaridade
- Utiliza similaridade de cosseno para encontrar notícias similares
- Compara os vetores TF-IDF das notícias para determinar a similaridade
- Gera um ranking das notícias mais similares para cada artigo

#### Cálculo de Popularidade
- Analisa o histórico de visualizações de todos os usuários
- Normaliza os scores de popularidade (0 a 1) baseado no número de visualizações
- Mantém um ranking atualizado das notícias mais populares

#### Sistema de Recomendação Híbrido
Para usuários cadastrados:
1. Analisa o último artigo lido pelo usuário
2. Busca artigos similares usando similaridade de conteúdo
3. Combina com artigos populares
4. Remove artigos já lidos pelo usuário
5. Retorna as top N recomendações

Para novos usuários:
- Retorna as notícias mais populares do momento

## Requisitos

- Python 3.9+
- Docker (opcional)

## Instalação e Execução

### Usando Python Local

1. Clone o repositório:
```bash
git clone <repository-url>
cd news_recommender
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Prepare a estrutura de dados:
```
news_recommender/
└── data/
    └── raw/
        ├── itens-parte*.csv    # Arquivos de notícias
        └── treino_parte*.csv   # Arquivos de usuários
```

5. Execute a aplicação:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Usando Docker

1. Construa a imagem:
```bash
docker build -t news-recommender .
```

2. Execute o container:
```bash
docker run -p 8000:8000 news-recommender
```

## API Endpoints

### 1. Recomendações Personalizadas
```
GET /recommend/{user_id}?n=5
```
- `user_id`: ID do usuário
- `n`: Número de recomendações (opcional, padrão=5)

### 2. Notícias Populares
```
GET /popular?n=5
```
- `n`: Número de notícias (opcional, padrão=5)

### 3. Status da API
```
GET /health
```

## Formato dos Dados

### Arquivo de Notícias (itens-parte*.csv)
- `Page`: ID único da notícia
- `title`: Título da notícia
- `body`: Corpo da notícia
- `url`: URL da notícia
- `caption`: Legenda (opcional)

### Arquivo de Usuários (treino_parte*.csv)
- `userId`: ID único do usuário
- `history`: Lista de IDs de notícias lidas, separadas por vírgula
- `historySize`: Número de notícias no histórico

## Cache e Persistência

- O modelo treinado é salvo em `models/recommender.pkl`
- Na inicialização, o sistema tenta carregar o modelo existente
- Se não encontrar, treina um novo modelo automaticamente

## Logging

O sistema mantém logs detalhados de:
- Carregamento de dados
- Treinamento do modelo
- Erros e exceções
- Requisições à API

## Tratamento de Erros

- Validação de entrada de dados
- Tratamento de usuários não encontrados
- Fallback para recomendações populares em caso de erro
- Retry automático no carregamento do modelo