# 🐦 Twitter Clone - Backend API

![Build Status](https://github.com/victorpiressk/twitter-clone-api/workflows/Backend%20CI/badge.svg)
![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-404%20passing-success)
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
- **Token Authentication** (DRF)
- **Pytest / Pytest-Django** (404 testes, 99% cobertura)
- **Docker & Docker Compose** (desenvolvimento cross-platform)
- **Black, Isort, Flake8** (qualidade de código)
- **GitHub Actions** (CI/CD)
- **Render** (deploy em produção)

---

## 📋 Funcionalidades

### Core Features
- ✅ Autenticação com Token (registro, login, logout)
- ✅ Gerenciamento de usuários e perfis completos
- ✅ Sistema de posts (criar, editar, listar, deletar)
- ✅ Curtidas e comentários
- ✅ Sistema de seguir/seguidores
- ✅ Feed personalizado

### Advanced Features
- ✅ **Retweets e Quote Retweets** - Compartilhe posts com ou sem comentário
- ✅ **Replies (Respostas)** - Threads de conversação completas
- ✅ **Múltiplas Mídias** - Até 4 imagens ou vídeos por post
- ✅ **Polls (Enquetes)** - Crie votações com 2-4 opções
- ✅ **Geolocalização** - Marque localização em posts
- ✅ **Posts Agendados** - Agende publicações futuras (Celery + Redis)
- ✅ **Views Counter** - Sistema de trending baseado em visualizações
- ✅ **Hashtags Automáticas** - Extração e indexação de hashtags
- ✅ **Notificações** - Sistema completo (likes, retweets, replies, follows, mentions)
- ✅ **Busca Avançada** - Busca global em posts, usuários e hashtags

### Quality & DevOps
- ✅ **404 testes automatizados** (99% cobertura)
- ✅ Pipeline de CI/CD com validação de qualidade
- ✅ Documentação completa de 52 endpoints

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
│   ├── serializers/
│   ├── views/
│   ├── tests/
│   └── urls.py
├── users/                     # Usuários, perfis e follows
│   ├── models/
│   │   ├── user.py           # User customizado
│   │   └── follow.py
│   ├── serializers/
│   │   ├── user_serializer.py
│   │   └── follow_serializer.py
│   ├── views/
│   ├── permissions/
│   ├── tests/
│   └── urls.py
├── posts/                     # Posts e features relacionadas
│   ├── models/
│   │   ├── post.py           # Post com retweets, replies, agendamento
│   │   ├── comment.py
│   │   ├── like.py
│   │   ├── postmedia.py      # Múltiplas mídias
│   │   ├── poll.py           # Polls completas
│   │   ├── location.py       # Geolocalização
│   │   ├── hashtag.py        # Sistema de hashtags
│   │   └── notification.py   # Notificações
│   ├── serializers/          # 10+ serializers organizados
│   │   ├── post_serializer.py
│   │   ├── comment_serializer.py
│   │   ├── like_serializer.py
│   │   ├── postmedia_serializer.py
│   │   ├── poll_serializer.py
│   │   ├── location_serializer.py
│   │   ├── hashtag_serializer.py
│   │   ├── notification_serializer.py
│   │   └── ...
│   ├── views/                # 14+ viewsets organizados
│   │   ├── post_views.py
│   │   ├── comment_views.py
│   │   ├── like_views.py
│   │   ├── retweet_views.py
│   │   ├── poll_views.py
│   │   ├── location_views.py
│   │   ├── hashtag_views.py
│   │   ├── notification_views.py
│   │   ├── search_views.py
│   │   └── ...
│   ├── tests/                # 345 testes organizados
│   │   ├── test_models/      # 10 arquivos
│   │   ├── test_serializers/ # 10 arquivos
│   │   ├── test_views/       # 14 arquivos
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
├── API_ENDPOINTS.md           # Documentação detalhada (52 endpoints)
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
docker-compose up -d

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

A documentação detalhada de **todos os 52 endpoints** da API está disponível em arquivo dedicado:

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
- Comentários (4 endpoints)
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
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Produção

Em produção (Render), as variáveis devem ser configuradas diretamente no painel do provedor, **sem uso de arquivo `.env`**.

---

## 🚀 Deploy em Produção

O deploy da aplicação é feito **sem Docker**, utilizando execução direta do Django com Gunicorn. Posts agendados são gerenciados por Celery workers no Render.

### Render (Configuração Atual)

#### 1. Criar Web Service (API Django)

**Build Command:**
```bash
poetry install --no-root && python manage.py collectstatic --noinput && python manage.py migrate
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

# Redis (Render Redis addon ou externo)
REDIS_URL=redis://<host-redis>:6379/0
CELERY_BROKER_URL=redis://<host-redis>:6379/0
CELERY_RESULT_BACKEND=redis://<host-redis>:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app
```

#### 5. Criar Serviços Necessários

- **PostgreSQL Database:** No Render, crie um PostgreSQL 14 database
- **Redis:** Adicione Redis addon do Render ou use serviço externo
- Conecte todos os serviços (Web Service + Workers + Database + Redis)

---

## 🧪 Testes

O projeto possui **404 testes automatizados** com **99% de cobertura**, organizados de forma modular.

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
# Rodar todos os testes
docker-compose exec backend pytest

# Com cobertura
docker-compose exec backend pytest --cov
```

### Estrutura de Testes

**Total:** 404 testes

- **Posts:** 345 testes
  - Models: ~100 testes (post, media, poll, location, hashtag, notification)
  - Serializers: ~80 testes
  - Views: ~94 testes (CRUD, retweets, replies, polls, search, etc)
  - Signals: ~15 testes (notificações automáticas)
  - Utils: ~10 testes (extração de hashtags)
  
- **Users:** ~40 testes
  - Models: user, follow
  - Serializers e Views
  
- **Authentication:** ~19 testes
  - Register, Login, Logout

**Organização modular:**
```
posts/tests/
├── test_models/         # 10 arquivos
├── test_serializers/    # 10 arquivos
├── test_views/          # 14 arquivos
└── conftest.py          # Fixtures compartilhadas
```

Os testes são executados **automaticamente no GitHub Actions** a cada push e pull request.

---

## 📄 CI/CD

### GitHub Actions

O projeto possui pipeline de CI/CD automatizado com dois workflows:

#### **Build & Test (`build.yml`):**
- ✅ Validação de código (Black, Isort, Flake8)
- ✅ Execução de 404 testes com PostgreSQL
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
    "last_name": "Usuário"
  }'
```

**Resposta:**
```json
{
  "user": {
    "id": 1,
    "username": "novouser",
    "email": "user@example.com",
    "first_name": "Novo",
    "last_name": "Usuário",
    "bio": "",
    "profile_image": null,
    "banner": null,
    "location": "",
    "website": "",
    "birth_date": null,
    "stats": {
      "posts": 0,
      "following": 0,
      "followers": 0
    },
    "created_at": "2026-02-19T10:00:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

#### 2. **Login:**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novouser",
    "password": "senha123"
  }'
```

**Resposta:** Mesma estrutura do registro

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

**Resposta:**
```json
{
  "detail": "Logout realizado com sucesso."
}
```

---

## 🗄️ Modelos de Dados

### User (Customizado)

```python
- username (unique)
- email (unique)
- first_name
- last_name
- bio (max 160 chars)
- profile_image (upload, max 2MB)
- banner (upload, max 5MB)          # ✨ NOVO
- location (CharField, max 100)      # ✨ NOVO
- website (URLField)                 # ✨ NOVO
- birth_date (DateField)             # ✨ NOVO
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
- image (optional upload) [DEPRECATED]
- is_retweet (Boolean)               # ✨ NOVO
- retweet_of (ForeignKey → Post)     # ✨ NOVO
- retweets_count (IntegerField)      # ✨ NOVO
- in_reply_to (ForeignKey → Post)    # ✨ NOVO
- scheduled_for (DateTimeField)      # ✨ NOVO
- views_count (IntegerField)         # ✨ NOVO
- location (ForeignKey → Location)   # ✨ NOVO
- hashtags (ManyToMany → Hashtag)    # ✨ NOVO
- created_at
- updated_at

# Properties computadas:
- likes_count
- comments_count
- is_published
```

### PostMedia (✨ NOVO)

```python
- post (ForeignKey → Post)
- type (CharField: image, video, gif)
- file (FileField)
- thumbnail (opcional)
- order (IntegerField)
- created_at
```

### Poll (✨ NOVO)

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

### PollOption (✨ NOVO)

```python
- poll (ForeignKey → Poll)
- text (CharField, max 100)
- votes (IntegerField, default 0)
- order (IntegerField)

# Properties computadas:
- percentage
```

### PollVote (✨ NOVO)

```python
- poll (ForeignKey → Poll)
- user (ForeignKey → User)
- option (ForeignKey → PollOption)
- created_at

# unique_together: (poll, user)
```

### Location (✨ NOVO)

```python
- name (CharField, max 200)
- latitude (DecimalField, opcional)
- longitude (DecimalField, opcional)
- created_at

# unique_together: (latitude, longitude)
# Properties computadas:
- has_coordinates
```

### Hashtag (✨ NOVO)

```python
- name (CharField, unique)
- slug (SlugField, unique)
- posts_count (IntegerField)
- created_at
```

### Notification (✨ NOVO)

```python
- recipient (ForeignKey → User)
- actor (ForeignKey → User)
- notification_type (CharField: like, retweet, reply, follow, mention)
- post (ForeignKey → Post, opcional)
- is_read (Boolean, default False)
- created_at

# unique_together: (recipient, actor, notification_type, post)
```

### Comment

```python
- user (ForeignKey → User)
- post (ForeignKey → Post)
- content (max 280 chars)
- created_at
- updated_at
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
- **Testes:** 404 (99% cobertura)
- **Endpoints:** 52
- **Models:** 11
- **Serializers:** 20+
- **ViewSets:** 14+
- **Arquivos de Teste:** 34

### Complexidade

- **Funcionalidades Avançadas:** 9 (polls, retweets, replies, etc)
- **Sistema de Notificações:** 5 tipos
- **Processamento Assíncrono:** Celery + Redis
- **Busca Avançada:** 3 tipos de recursos

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
    'http://localhost:3000'
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

// Login
const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login/', { username, password });
  localStorage.setItem('token', response.data.token);
  return response.data.user;
};

// Criar post com poll
const createPost = async (content: string, pollData?: PollData) => {
  const response = await api.post('/posts/', {
    content,
    poll: pollData ? {
      duration_hours: pollData.duration,
      options: pollData.options
    } : undefined
  });
  return response.data;
};

// Upload de múltiplas imagens
const createPostWithImages = async (content: string, images: File[]) => {
  const formData = new FormData();
  formData.append('content', content);
  images.forEach(img => formData.append('media_files', img));
  
  const response = await api.post('/posts/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
};

// Busca global
const search = async (query: string) => {
  const response = await api.get(`/search/all/?q=${query}&limit=5`);
  return response.data; // { posts: [], users: [], hashtags: [], meta: {} }
};

// Notificações não lidas
const getUnreadCount = async () => {
  const response = await api.get('/notifications/unread-count/');
  return response.data.count;
};
```

---

## 🎯 Casos de Uso Principais

### 1. Criar Post com Recursos Avançados

```python
POST /api/posts/
{
  "content": "Explorando #Python e #Django no Brasil! 🇧🇷",
  "media_files": [<imagem1>, <imagem2>],
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
- Post criado com 2 imagens
- Localização marcada
- Poll ativa com 4 opções
- Hashtags extraídas automaticamente (#Python, #Django)
- Publicação agendada via Celery

### 2. Interagir com Posts

```python
# Retweet simples
POST /api/posts/{id}/retweet/

# Quote retweet
POST /api/posts/{id}/quote-retweet/
{ "content": "Concordo!" }

# Reply
POST /api/posts/
{ "content": "Ótimo post!", "in_reply_to": {id} }

# Ver thread completa
GET /api/posts/{id}/thread/
```

### 3. Sistema de Notificações

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

### 4. Busca e Descoberta

```python
# Busca global
GET /api/search/all/?q=python&limit=5
# Retorna: posts, users, hashtags

# Trending hashtags
GET /api/hashtags/trending/?period=week&limit=10

# Posts mais vistos
GET /api/posts/trending/?period=today&limit=20

# Posts por hashtag
GET /api/hashtags/{id}/posts/

# Locations próximas
GET /api/locations/nearby/?lat=-23.55&lng=-46.63&radius=10
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

### Qualidade

- ✅ 404 testes automatizados (99% cobertura)
- ✅ Pipeline de CI/CD em cada commit
- ✅ Code review automatizado
- ✅ Padrões rigorosos de código

### Performance

- ✅ Queries otimizadas com `select_related` e `prefetch_related`
- ✅ Paginação em todas as listagens
- ✅ Índices em campos críticos (created_at, views_count, etc)
- ✅ Processamento assíncrono para tarefas pesadas

### Escalabilidade

- ✅ Arquitetura modular e desacoplada
- ✅ Celery para processamento distribuído
- ✅ Redis para cache e filas
- ✅ Fácil adicionar novos workers

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
  - Deploy em produção
  - Docker para desenvolvimento
  - Arquitetura modular e escalável

**Ideal para demonstrar em entrevistas:**
- Clean code e boas práticas
- Testes e qualidade
- DevOps e CI/CD
- Features complexas (polls, retweets, notificações)
- Processamento assíncrono

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
- Certifique-se que os testes passam (`pytest`)
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

### Tutoriais e Referências
- [DRF Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
- [Celery with Django](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)

---

## 🔄 Changelog

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

## ⭐ Se Este Projeto Te Ajudou

**Considere dar uma estrela no GitHub!**

[![GitHub stars](https://img.shields.io/github/stars/victorpiressk/twitter-clone-api?style=social)](https://github.com/victorpiressk/twitter-clone-api)

---

## 📞 Suporte

Para dúvidas ou suporte:
- Abra uma [issue](https://github.com/victorpiressk/twitter-clone-api/issues)
- Entre em contato via [LinkedIn](https://www.linkedin.com/in/victor-p-rego/)

---

**Versão:** 2.0.0  
**Última atualização:** 19/02/2026  
**Status:** ✅ Em Produção  
**Documentação:** Completa e Atualizada
