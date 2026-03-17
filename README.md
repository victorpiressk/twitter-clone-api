# 🐦 Twitter Clone - Backend API

![Build Status](https://github.com/victorpiressk/twitter-clone-api/workflows/Backend%20CI/badge.svg)
![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-414%20passing-success)
![Python](https://img.shields.io/badge/python-3.14.0-blue)
![Django](https://img.shields.io/badge/django-6.0-green)

API REST completa desenvolvida com Django e Django REST Framework para uma rede social inspirada no Twitter, com recursos avançados de mídia, enquetes, geolocalização e muito mais.

---

## 🚀 Tecnologias

- **Python 3.14.0**
- **Django 6.0**
- **Django REST Framework 3.16.1**
- **Poetry 2.2.1** (gerenciamento de dependências)
- **PostgreSQL 14** (desenvolvimento e produção)
- **Celery + Redis** (processamento assíncrono e agendamento)
- **Cloudinary** (armazenamento de mídia em produção)
- **Token Authentication** (DRF)
- **Pytest / Pytest-Django** (414 testes, 99% cobertura)
- **Docker & Docker Compose** (desenvolvimento cross-platform)
- **Black, Isort, Flake8** (qualidade de código)
- **GitHub Actions** (CI/CD)
- **Render** (deploy em produção)

---

## 📋 Funcionalidades

### Core Features
- ✅ Autenticação com Token (registro, login, logout)
- ✅ Login com username, email ou telefone
- ✅ Gerenciamento de usuários e perfis completos
- ✅ Sistema de posts (criar, editar, listar, deletar)
- ✅ Curtidas com persistência de estado
- ✅ Sistema de seguir/seguidores
- ✅ Feed personalizado

### Advanced Features
- ✅ **Retweets e Quote Retweets** - Retweet simples e quote retweet independentes
- ✅ **Replies (Respostas)** - Threads de conversação completas
- ✅ **Múltiplas Mídias** - Até 4 arquivos por post (imagens, GIFs, vídeos)
- ✅ **Polls (Enquetes)** - Crie votações com 2-4 opções
- ✅ **Geolocalização** - Marque localização em posts
- ✅ **Posts Agendados** - Agende publicações futuras (Celery + Redis)
- ✅ **Views Counter** - Sistema de trending baseado em visualizações
- ✅ **Hashtags Automáticas** - Extração e indexação de hashtags
- ✅ **Notificações** - Sistema completo (likes, retweets, replies, follows, mentions)
- ✅ **Busca Avançada** - Busca global em posts, usuários e hashtags
- ✅ **Filtros Dinâmicos** - Filtrar posts por autor, mídia, replies, retweets e curtidas
- ✅ **Cloudinary** - Armazenamento persistente de mídia em produção

### Quality & DevOps
- ✅ **414 testes automatizados** (99% cobertura)
- ✅ Pipeline de CI/CD com validação de qualidade
- ✅ Documentação completa de 47 endpoints

---

## 📂 Estrutura do Projeto

```
twitter-clone-api/
├── config/                    # Configurações do Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py             # Configuração Celery
├── authentication/            # Sistema de autenticação
│   ├── serializers/          # 2 serializers
│   ├── views/                # 3 views
│   ├── tests/
│   └── urls.py
├── users/                     # Usuários, perfis e follows
│   ├── models/               # 2 models (user, follow)
│   ├── serializers/          # 2 serializers
│   ├── views/                # 2 views
│   ├── permissions/
│   ├── tests/
│   └── urls.py
├── posts/                     # Posts e features relacionadas
│   ├── models/               # 7 models
│   │   ├── post.py           # Post com retweets, replies, agendamento
│   │   ├── like.py
│   │   ├── postmedia.py      # Múltiplas mídias
│   │   ├── poll.py           # Polls completas
│   │   ├── location.py       # Geolocalização
│   │   ├── hashtag.py        # Sistema de hashtags
│   │   └── notification.py   # Notificações
│   ├── serializers/          # 6 serializers
│   ├── views/                # 7 viewsets
│   │   ├── post_views.py
│   │   ├── like_views.py
│   │   ├── retweet_views.py
│   │   ├── poll_views.py
│   │   ├── location_views.py
│   │   ├── hashtag_views.py
│   │   ├── notification_views.py
│   │   └── search_views.py
│   ├── tests/                # 414 testes organizados
│   │   ├── test_models/
│   │   ├── test_serializers/
│   │   ├── test_views/
│   │   └── conftest.py
│   ├── signals.py            # Notificações automáticas
│   ├── utils.py              # Extração de hashtags
│   ├── tasks.py              # Tarefas Celery (posts agendados)
│   └── urls.py
├── .github/workflows/         # CI/CD (GitHub Actions)
│   ├── build.yml
│   └── code-review.yml
├── Dockerfile                 # Imagem Docker (desenvolvimento)
├── docker-compose.yml         # Orquestração (backend, db, redis, celery)
├── Makefile                   # Comandos úteis
├── pyproject.toml             # Dependências Poetry
├── .env.example               # Template de variáveis de ambiente
├── API_ENDPOINTS.md           # Documentação detalhada (47 endpoints)
├── README_DOCKER.md           # Documentação do Docker + Celery
└── manage.py
```

---

## 🔧 Instalação Local (sem Docker)

### Pré-requisitos
- Python 3.14.0
- Poetry 2.2.1+
- PostgreSQL 14+
- Redis (para posts agendados)

### Passos

```bash
# 1. Clone o repositório
git clone https://github.com/victorpiressk/twitter-clone-api.git
cd twitter-clone-api

# 2. Instale Poetry (se não tiver)
pip install poetry==2.2.1

# 3. Instale dependências
poetry install

# 4. Ative o ambiente virtual
poetry shell

# 5. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# 6. Execute migrations
poetry run python manage.py migrate

# 7. (Opcional) Crie um superusuário
poetry run python manage.py createsuperuser

# 8. Inicie Redis (em outro terminal)
redis-server

# 9. Inicie Celery Worker (em outro terminal)
poetry run celery -A config worker -l info

# 10. Inicie Celery Beat (agendador - em outro terminal)
poetry run celery -A config beat -l info

# 11. Inicie o servidor Django
poetry run python manage.py runserver
```

**A API estará disponível em:** `http://localhost:8000`

---

## 🐳 Desenvolvimento com Docker (Recomendado)

Este projeto utiliza Docker **para desenvolvimento local**, garantindo ambiente consistente com todos os serviços necessários (PostgreSQL, Redis, Celery).

### Quick Start

```bash
# 1. Build e iniciar todos os containers
docker-compose up -d --build

# 2. Executar migrations
docker-compose exec backend python manage.py migrate

# 3. Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# 4. Verificar status dos serviços
docker-compose ps
```

### Serviços Disponíveis

```yaml
backend:    http://localhost:8000  # API Django
db:         localhost:5432          # PostgreSQL
redis:      localhost:6379          # Redis
celery:     (worker background)     # Processamento assíncrono
celery-beat: (scheduler background) # Agendador de tasks
```

### 📘 Documentação Completa do Docker

Para instruções detalhadas sobre Docker, Celery, comandos úteis e troubleshooting:

👉 **[README_DOCKER.md](./README_DOCKER.md)**

---

## 📡 Documentação da API

A documentação detalhada de **todos os 47 endpoints** da API está disponível em arquivo dedicado:

👉 **[API_ENDPOINTS.md](./API_ENDPOINTS.md)**

**Inclui:**
- ✅ Rotas e métodos HTTP
- ✅ Parâmetros e body
- ✅ Exemplos de request/response completos
- ✅ Validações e regras de negócio
- ✅ Códigos de status
- ✅ Exemplos práticos em cURL, Python e JavaScript

**Recursos documentados:**
- Autenticação (3 endpoints)
- Usuários (6 endpoints)
- Follows (3 endpoints)
- Posts CRUD + Feed (6 endpoints)
- Retweets (3 endpoints)
- Replies (3 endpoints)
- Múltiplas Mídias (integrado ao create post)
- Posts Agendados (1 endpoint)
- Trending (1 endpoint)
- Polls (4 endpoints)
- Locations (4 endpoints)
- Hashtags (5 endpoints)
- Notificações (5 endpoints)
- Busca (1 endpoint)
- Curtidas (3 endpoints)

---

## ⚙️ Variáveis de Ambiente

O projeto utiliza variáveis de ambiente para configuração.

### Desenvolvimento Local

Copie o arquivo `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

**Variáveis principais:**

```env
# Django
DEBUG=True
SECRET_KEY=sua-chave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=twitter_clone_api_dev_db
SQL_USER=seu_usuario
SQL_PASSWORD=sua_senha
SQL_HOST=db  # ou localhost se não usar Docker
SQL_PORT=5432

# Redis (Posts Agendados)
REDIS_URL=redis://redis:6379/0  # ou redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Produção

Em produção (Render), as variáveis devem ser configuradas diretamente no painel do provedor, **sem uso de arquivo `.env`**.

**Variáveis adicionais obrigatórias em produção:**

```env
# Cloudinary (armazenamento de mídia)
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

---

## 🚀 Deploy em Produção

O deploy da aplicação é feito **sem Docker**, utilizando execução direta do Django com Gunicorn. Posts agendados são gerenciados por Celery workers no Render.

### Render (Configuração Atual)

#### 1. Criar Web Service (API Django)

**Build Command:**
```bash
poetry install --no-root && python manage.py collectstatic --noinput --upload-unhashed-files && python manage.py migrate
```

**Start Command:**
```bash
poetry run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

#### 2. Criar Background Worker (Celery Worker)

**Start Command:**
```bash
poetry run celery -A config worker -l info
```

#### 3. Criar Background Worker (Celery Beat - Agendador)

**Start Command:**
```bash
poetry run celery -A config beat -l info
```

#### 4. Configurar Variáveis de Ambiente

No painel do Render, adicione:

```env
# Django
DEBUG=False
SECRET_KEY=<gerar-chave-segura-com-django>
ALLOWED_HOSTS=seu-dominio.onrender.com

# Database
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=<nome-do-banco>
SQL_USER=<usuario>
SQL_PASSWORD=<senha>
SQL_HOST=<host-interno-do-render>
SQL_PORT=5432

# Redis
REDIS_URL=redis://<host-redis>:6379/0
CELERY_BROKER_URL=redis://<host-redis>:6379/0
CELERY_RESULT_BACKEND=redis://<host-redis>:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app

# Cloudinary (obrigatório para mídia em produção)
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

#### 5. Criar Serviços Necessários

- **PostgreSQL Database:** No Render, crie um PostgreSQL 14 database
- **Redis:** Adicione Redis addon do Render ou use serviço externo
- **Cloudinary:** Crie conta em [cloudinary.com](https://cloudinary.com) e obtenha as credenciais
- Conecte todos os serviços (Web Service + Workers + Database + Redis)

---

## 🧪 Testes

O projeto possui **414 testes automatizados** com **99% de cobertura**, organizados de forma modular.

### Executar Testes

```bash
# Rodar todos os testes
poetry run pytest

# Testes com cobertura
poetry run pytest --cov --cov-report=html

# Ver relatório de cobertura
# Abrir: htmlcov/index.html

# Rodar testes específicos
poetry run pytest posts/tests/test_models/
poetry run pytest posts/tests/test_views/test_poll_views.py
```

### Com Docker

```bash
# Rodar todos os testes (primeira execução ou após mudanças nos models)
docker-compose exec backend pytest --create-db -v

# Execuções subsequentes (reutiliza banco de teste existente)
docker-compose exec backend pytest -v

# Com cobertura
docker-compose exec backend pytest --cov
```

> **Nota:** Use `--create-db` sempre que houver mudanças nos models ou migrations, pois o pytest-django reutiliza o banco de teste por padrão.

### Estrutura de Testes

**Total:** 414 testes

- **Posts:** testes de models, serializers, views, signals e utils
- **Users:** testes de models, serializers e views
- **Authentication:** testes de registro, login e logout

**Organização modular:**
```
posts/tests/
├── test_models/
├── test_serializers/
├── test_views/
└── conftest.py       # Fixtures compartilhadas
```

Os testes são executados **automaticamente no GitHub Actions** a cada push e pull request.

---

## 📄 CI/CD

### GitHub Actions

O projeto possui pipeline de CI/CD automatizado com dois workflows:

#### **Build & Test (`build.yml`):**
- ✅ Validação de código (Black, Isort, Flake8)
- ✅ Execução de 414 testes com PostgreSQL
- ✅ Relatório de cobertura (99%)
- ✅ Build da imagem Docker para validação
- ✅ Matrix testing (múltiplas versões Python/Django)

#### **Code Review (`code-review.yml`):**
- ✅ Análise estática de código
- ✅ Verificação de formatação
- ✅ Organização de imports
- ✅ Segurança e boas práticas

**Os workflows são executados em:**
- Pushes para `main` e `develop`
- Pull requests para qualquer branch

**Status:** ![Build Status](https://github.com/victorpiressk/twitter-clone-api/workflows/Backend%20CI/badge.svg)

---

## 🧹 Qualidade de Código

O projeto segue rigorosos padrões de qualidade:

```bash
# Formatação automática
poetry run black .

# Organização de imports
poetry run isort .

# Verificação de lint
poetry run flake8 .

# Rodar todos os checks
poetry run black . && poetry run isort . && poetry run flake8 .
```

**Com Docker:**
```bash
docker-compose exec backend black .
docker-compose exec backend isort .
docker-compose exec backend flake8 .
```

**Padrões:**
- Black (formatação)
- Isort (imports)
- Flake8 (linting)
- Line length: 88 caracteres
- Import order: stdlib → third-party → local

Essas verificações fazem parte do pipeline de CI e bloqueiam merges com problemas.

---

## 🛠️ Admin do Django

### Criar superusuário:

**Local:**
```bash
poetry run python manage.py createsuperuser
```

**Docker:**
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Acessar:
```
http://localhost:8000/admin
```

**Recursos administráveis:**
- Usuários e perfis
- Posts, retweets, replies
- Polls e votações
- Locations
- Hashtags
- Notificações
- Follows

---

## 🔐 Autenticação

A API usa **Token Authentication** do Django REST Framework.

### Fluxo de Autenticação

#### 1. **Registro:**

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novouser",
    "email": "user@example.com",
    "password": "senha123",
    "password_confirm": "senha123",
    "first_name": "Novo",
    "last_name": "Usuário",
    "birth_date": "1995-06-15"
  }'
```

#### 2. **Login (username, email ou telefone):**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "novouser",
    "password": "senha123"
  }'
```

#### 3. **Usar o token em requisições:**

```bash
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Token SEU_TOKEN_AQUI"
```

#### 4. **Logout:**

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token SEU_TOKEN_AQUI"
```

---

## 🗄️ Modelos de Dados

### User (Customizado)

```python
- username (unique)
- email (unique, opcional)
- phone (unique, opcional)        # login por telefone
- first_name
- last_name
- bio (max 160 chars)
- profile_image (Cloudinary, max 5MB)
- banner (Cloudinary, max 5MB)
- location (CharField, max 100)
- website (URLField)
- birth_date (DateField, obrigatório, mín. 13 anos)
- created_at
- updated_at

# Properties computadas:
- followers_count
- following_count
- posts_count
```

### Post

```python
- author (ForeignKey → User)
- content (max 280 chars)
- is_retweet (Boolean)
- retweet_of (ForeignKey → Post)
- retweets_count (IntegerField)
- in_reply_to (ForeignKey → Post)
- scheduled_for (DateTimeField)
- views_count (IntegerField)
- location (ForeignKey → Location)
- hashtags (ManyToMany → Hashtag)
- created_at
- updated_at

# Properties computadas:
- likes_count
- replies_count
- is_published
```

### PostMedia

```python
- post (ForeignKey → Post)
- type (CharField: image, video, gif)
- file (FileField → Cloudinary em produção)
- thumbnail (opcional)
- order (IntegerField)
- created_at
```

### Poll

```python
- post (OneToOne → Post)
- question (CharField, max 280)
- duration_hours (IntegerField, 1-168)
- ends_at (DateTimeField)
- created_at

# Properties computadas:
- total_votes
- is_ended
```

### PollOption

```python
- poll (ForeignKey → Poll)
- text (CharField, max 100)
- votes (IntegerField, default 0)
- order (IntegerField)

# Properties computadas:
- percentage
```

### PollVote

```python
- poll (ForeignKey → Poll)
- user (ForeignKey → User)
- option (ForeignKey → PollOption)
- created_at

# unique_together: (poll, user)
```

### Location

```python
- name (CharField, max 200)
- latitude (DecimalField, opcional)
- longitude (DecimalField, opcional)
- created_at

# unique_together: (latitude, longitude)
# Properties computadas:
- has_coordinates
```

### Hashtag

```python
- name (CharField, unique)
- slug (SlugField, unique)
- posts_count (IntegerField)
- created_at
```

### Notification

```python
- recipient (ForeignKey → User)
- actor (ForeignKey → User)
- notification_type (CharField: like, retweet, reply, follow, mention)
- post (ForeignKey → Post, opcional)
- is_read (Boolean, default False)
- created_at

# unique_together: (recipient, actor, notification_type, post)
```

### Like

```python
- user (ForeignKey → User)
- post (ForeignKey → Post)
- created_at

# unique_together: (user, post)
```

### Follow

```python
- follower (ForeignKey → User)
- following (ForeignKey → User)
- created_at

# unique_together: (follower, following)
```

---

## 📊 Estatísticas do Projeto

### Métricas de Código

- **Linhas de Código:** ~8.000+ (Python)
- **Testes:** 414 (99% cobertura)
- **Endpoints:** 47
- **Models:** 9
- **Serializers:** 10
- **ViewSets:** 12
- **Arquivos de Teste:** 30+

### Complexidade

- **Funcionalidades Avançadas:** 10 (polls, retweets, replies, filtros dinâmicos, etc)
- **Sistema de Notificações:** 5 tipos
- **Processamento Assíncrono:** Celery + Redis
- **Busca Avançada:** 3 tipos de recursos
- **Armazenamento de Mídia:** Cloudinary (produção)

---

## 🔗 Integração com Frontend

Este backend foi projetado para integração com aplicações frontend modernas.

### Stack Recomendada

- **Framework:** React / Next.js / Vue / Angular
- **TypeScript:** Tipagem forte
- **HTTP Client:** Axios / Fetch API / SWR / React Query
- **State Management:** Redux / Zustand / Context API
- **Styling:** TailwindCSS / Styled Components

### Comunicação

- **Protocolo:** REST API
- **Autenticação:** Token no header `Authorization: Token <token>`
- **CORS:** Configurado para origens específicas

### Configurar CORS em Produção

No `config/settings.py`:

```python
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:5173'
).split(',')
```

Adicione seu domínio frontend nas variáveis de ambiente:

```env
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app,https://outro-dominio.com
```

### Exemplo de Integração (React + Axios)

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://sua-api.onrender.com/api',
});

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Login com username, email ou telefone
const login = async (identifier: string, password: string) => {
  const response = await api.post('/auth/login/', { identifier, password });
  localStorage.setItem('token', response.data.token);
  return response.data.user;
};

// Listar posts com filtros dinâmicos
const getUserPosts = async (userId: number) => {
  const response = await api.get('/posts/', {
    params: { author: userId, has_reply: false, is_retweet: false }
  });
  return response.data;
};

// Posts curtidos por um usuário
const getLikedPosts = async (userId: number) => {
  const response = await api.get('/posts/', {
    params: { liked_by: userId }
  });
  return response.data;
};

// Upload de mídia (imagens e GIFs)
const createPostWithMedia = async (content: string, files: File[]) => {
  const formData = new FormData();
  formData.append('content', content);
  files.forEach(file => formData.append('media_files', file));

  const response = await api.post('/posts/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Curtir post — retorna like_id necessário para descurtir
const likePost = async (postId: number) => {
  const response = await api.post('/likes/', { post: postId });
  return response.data; // { id: likeId, ... }
};

// Descurtir post usando like_id
const unlikePost = async (likeId: number) => {
  await api.delete(`/likes/${likeId}/`);
};
```

---

## 🎯 Casos de Uso Principais

### 1. Criar Post com Recursos Avançados

```python
POST /api/posts/
{
  "content": "Explorando #Python e #Django no Brasil! 🇧🇷",
  "media_files": [<imagem1>, <gif1>],
  "location": {
    "name": "São Paulo, Brasil",
    "latitude": "-23.550520",
    "longitude": "-46.633308"
  },
  "poll": {
    "question": "Qual você prefere?",
    "duration_hours": 24,
    "options": ["Python", "JavaScript", "Go", "Rust"]
  },
  "scheduled_for": "2026-02-20T15:00:00Z"
}
```

**Resultado:**
- Post criado com 1 imagem e 1 GIF (armazenados no Cloudinary em produção)
- Localização marcada
- Poll ativa com 4 opções
- Hashtags extraídas automaticamente (#Python, #Django)
- Publicação agendada via Celery

### 2. Interagir com Posts

```python
# Retweet simples (independente de quote retweet existente)
POST /api/posts/{id}/retweet/

# Quote retweet (múltiplos permitidos)
POST /api/posts/{id}/quote-retweet/
{ "content": "Concordo!" }

# Desfazer apenas retweet simples
DELETE /api/posts/{id}/unretweet/

# Reply
POST /api/posts/
{ "content": "Ótimo post!", "in_reply_to": {id} }

# Ver thread completa
GET /api/posts/{id}/thread/
```

### 3. Filtros Dinâmicos de Posts

```python
# Posts de um usuário (sem replies e sem retweets)
GET /api/posts/?author=1&has_reply=false&is_retweet=false

# Replies de um usuário
GET /api/posts/?author=1&has_reply=true

# Posts com mídia de um usuário
GET /api/posts/?author=1&has_media=true

# Posts curtidos por um usuário
GET /api/posts/?liked_by=1
```

### 4. Sistema de Notificações

```python
# Listar notificações
GET /api/notifications/

# Não lidas
GET /api/notifications/unread/

# Contador
GET /api/notifications/unread-count/

# Marcar como lida
POST /api/notifications/{id}/read/

# Marcar todas
POST /api/notifications/read-all/
```

**Notificações automáticas via Signals:**
- Alguém curtiu seu post → notificação
- Alguém retweetou → notificação
- Alguém respondeu → notificação
- Alguém te seguiu → notificação
- Alguém te mencionou → notificação

### 5. Busca e Descoberta

```python
# Busca global
GET /api/search/all/?q=python&limit=5
# Retorna: posts, users, hashtags

# Trending hashtags
GET /api/hashtags/trending/?period=week&limit=10

# Posts mais vistos
GET /api/posts/trending/?period=today&limit=20
```

---

## 📌 Observações Importantes

### Desenvolvimento

- ✅ Docker é utilizado **exclusivamente para desenvolvimento**
- ✅ Inclui todos os serviços necessários (DB, Redis, Celery)
- ✅ Hot reload habilitado para agilizar desenvolvimento
- ✅ Volumes persistem dados entre restarts

### Produção

- ✅ Aplicação roda **diretamente via Python + Gunicorn**
- ✅ Celery workers em background services separados
- ✅ Redis gerenciado (Render addon ou serviço externo)
- ✅ PostgreSQL gerenciado (Render database)
- ✅ Mídia armazenada no **Cloudinary** (obrigatório em produção)

### Mídia

- Em **produção**, todos os uploads são armazenados no **Cloudinary**
- URLs de mídia em produção seguem o padrão: `https://res.cloudinary.com/{cloud_name}/...`
- Em **desenvolvimento local**, arquivos são armazenados em `/media/`
- Limites: imagens 5MB, GIFs 15MB, vídeos 50MB, máximo 4 arquivos por post

### Qualidade

- ✅ 414 testes automatizados (99% cobertura)
- ✅ Pipeline de CI/CD em cada commit
- ✅ Code review automatizado
- ✅ Padrões rigorosos de código

### Performance

- ✅ Queries otimizadas com `select_related` e `prefetch_related`
- ✅ Paginação em todas as listagens
- ✅ Índices em campos críticos (created_at, views_count, etc)
- ✅ Processamento assíncrono para tarefas pesadas

---

## 🎓 Projeto Educacional & Portfólio

Este projeto foi desenvolvido como:

- ✅ **Projeto final de curso** completo
- ✅ **Portfólio backend** profissional
- ✅ **Demonstração de skills** avançadas:
  - Django & DRF avançado
  - Celery + Redis
  - Testes automatizados
  - CI/CD com GitHub Actions
  - Deploy em produção (Render + Cloudinary)
  - Docker para desenvolvimento
  - Arquitetura modular e escalável

---

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais.

---

## 👨‍💻 Autor

**Victor Pires**

- GitHub: [@victorpiressk](https://github.com/victorpiressk)
- LinkedIn: [in/victor-p-rego](https://www.linkedin.com/in/victor-p-rego/)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commitar suas mudanças (`git commit -m 'feat: adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

**Por favor:**
- Siga os padrões de código (Black, Isort, Flake8)
- Adicione testes para novas funcionalidades (manter 99% cobertura)
- Atualize a documentação quando necessário
- Certifique-se que os testes passam (`pytest --create-db`)
- Verifique o CI antes de fazer merge

---

## 🐛 Reportar Bugs

Encontrou um bug? Abra uma issue com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Screenshots (se aplicável)
- Ambiente (OS, Python version, etc)

---

## 📚 Recursos Adicionais

### Documentação Oficial
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Cloudinary Documentation](https://cloudinary.com/documentation)

---

## 🔄 Changelog

### v3.0.0 (2026-03-16)
- ✨ Login com username, email ou telefone (`identifier`)
- ✨ Campo `phone` adicionado ao modelo User
- ✨ Remoção do modelo Comment (substituído por Replies)
- ✨ `stats.comments` renomeado para `stats.replies`
- ✨ Persistência de likes com `is_liked` e `like_id` no serializer de posts
- ✨ Correção do comportamento de retweets (simples e quote independentes)
- ✨ Filtros dinâmicos em `GET /api/posts/` (`author`, `has_reply`, `has_media`, `is_retweet`, `liked_by`)
- ✨ Integração com Cloudinary para armazenamento de mídia em produção
- ✨ Aumento do limite de GIFs para 15MB
- ✨ Aumento do limite de `profile_image` para 5MB
- 🧪 Expandido testes de 404 para 414
- 📚 Atualizada documentação (v3.0, 47 endpoints)

### v2.0.0 (2026-02-19)
- ✨ Adicionado sistema de Retweets e Quote Retweets
- ✨ Adicionado sistema de Replies (threads)
- ✨ Implementado upload de múltiplas mídias (até 4 por post)
- ✨ Criado sistema completo de Polls
- ✨ Adicionado geolocalização de posts
- ✨ Implementado posts agendados (Celery + Redis)
- ✨ Criado sistema de views counter e trending
- ✨ Implementado hashtags automáticas
- ✨ Criado sistema completo de notificações
- ✨ Adicionado busca avançada global
- 🧪 Expandido testes de 83 para 404
- 📚 Atualizada documentação completa

### v1.0.0 (2026-01-08)
- 🎉 Release inicial
- ✅ Autenticação com Token
- ✅ CRUD de usuários e posts
- ✅ Sistema de follows
- ✅ Curtidas e comentários
- ✅ Feed personalizado
- ✅ 83 testes automatizados

---

**Versão:** 3.0.0  
**Última atualização:** 16/03/2026  
**Status:** ✅ Em Produção  
**Documentação:** Completa e Atualizada