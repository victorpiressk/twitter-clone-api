# 🐦 Twitter Clone - Backend API

![Build Status](https://github.com/victorpiressk/twitter-clone-api/workflows/Backend%20CI/badge.svg)
![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-427%20passing-success)
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
- **Pytest / Pytest-Django** (427 testes, 99% cobertura)
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
- ✅ **Configurações da Conta** — alteração de email, phone, username e senha
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
- ✅ **427 testes automatizados** (99% cobertura)
- ✅ Pipeline de CI/CD com validação de qualidade
- ✅ Documentação completa de 49 endpoints

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
│   ├── serializers/          # 4 serializers
│   ├── views/                # 2 views
│   ├── permissions/
│   ├── tests/
│   └── urls.py
├── posts/                     # Posts e features relacionadas
│   ├── models/               # 7 models
│   │   ├── post.py
│   │   ├── like.py
│   │   ├── postmedia.py
│   │   ├── poll.py
│   │   ├── location.py
│   │   ├── hashtag.py
│   │   └── notification.py
│   ├── serializers/          # 6 serializers
│   ├── views/                # 7 viewsets
│   ├── tests/                # 427 testes organizados
│   │   ├── test_models/
│   │   ├── test_serializers/
│   │   ├── test_views/
│   │   └── conftest.py
│   ├── signals.py
│   ├── utils.py
│   ├── tasks.py
│   └── urls.py
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── .env.example
├── API_ENDPOINTS.md           # Documentação detalhada (49 endpoints)
├── README_DOCKER.md
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
backend:     http://localhost:8000  # API Django
db:          localhost:5432          # PostgreSQL
redis:       localhost:6379          # Redis
celery:      (worker background)     # Processamento assíncrono
celery-beat: (scheduler background)  # Agendador de tasks
```

👉 **[README_DOCKER.md](./README_DOCKER.md)** — instruções detalhadas sobre Docker e Celery

---

## 📡 Documentação da API

A documentação detalhada de **todos os 49 endpoints** está disponível em:

👉 **[API_ENDPOINTS.md](./API_ENDPOINTS.md)**

**Recursos documentados:**
- Autenticação (3 endpoints)
- Usuários (6 endpoints)
- Follows (3 endpoints)
- Posts CRUD + Feed (6 endpoints)
- Retweets (3 endpoints)
- Replies (3 endpoints)
- Posts Agendados (1 endpoint)
- Trending (1 endpoint)
- Polls (4 endpoints)
- Locations (4 endpoints)
- Hashtags (5 endpoints)
- Notificações (5 endpoints)
- Busca (1 endpoint)
- Curtidas (3 endpoints)
- Configurações da Conta (2 endpoints)

---

## ⚙️ Variáveis de Ambiente

### Desenvolvimento Local

```bash
cp .env.example .env
```

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
SQL_HOST=db
SQL_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Produção

```env
# Django
DEBUG=False
SECRET_KEY=<gerar-chave-segura>
ALLOWED_HOSTS=seu-dominio.onrender.com

# Database, Redis, CORS...

# Cloudinary (obrigatório para mídia em produção)
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret
```

---

## 🚀 Deploy em Produção (Render)

#### Build Command:
```bash
poetry install --no-root && python manage.py collectstatic --noinput --upload-unhashed-files && python manage.py migrate
```

#### Start Command:
```bash
poetry run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

#### Celery Worker:
```bash
poetry run celery -A config worker -l info
```

#### Celery Beat:
```bash
poetry run celery -A config beat -l info
```

**Serviços necessários:** PostgreSQL 14, Redis, Cloudinary

---

## 🧪 Testes

O projeto possui **427 testes automatizados** com **99% de cobertura**.

### Executar Testes

```bash
# Local
poetry run pytest

# Com cobertura
poetry run pytest --cov --cov-report=html
```

### Com Docker

```bash
# Primeira execução ou após mudanças nos models
docker-compose exec backend pytest --create-db -v

# Execuções subsequentes
docker-compose exec backend pytest -v
```

> **Nota:** Use `--create-db` sempre que houver mudanças nos models ou migrations.

---

## 📄 CI/CD

### GitHub Actions

- **Build & Test:** validação de código, 427 testes, cobertura 99%
- **Code Review:** análise estática, formatação, imports, segurança

Executado em pushes para `main` e `develop`, e em pull requests.

---

## 🧹 Qualidade de Código

```bash
poetry run black . && poetry run isort . && poetry run flake8 .
```

---

## 🔐 Autenticação

### Login (username, email ou telefone):

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"novouser","password":"senha123"}'
```

### Usar token:

```bash
curl -X GET http://localhost:8000/api/posts/ \
  -H "Authorization: Token SEU_TOKEN_AQUI"
```

---

## 🗄️ Modelos de Dados

### User
```python
- username, email, phone (únicos, editáveis via /account/)
- first_name, last_name, bio, location, website
- profile_image, banner (Cloudinary, max 5MB)
- birth_date (obrigatório, mín. 13 anos)
- created_at, updated_at
```

### Post
```python
- author, content (max 280), is_retweet, retweet_of
- in_reply_to, scheduled_for, views_count
- location, hashtags
- replies_count, likes_count, is_published (computed)
```

### PostMedia, Poll, PollOption, PollVote, Location, Hashtag, Notification, Like, Follow

---

## 📊 Estatísticas do Projeto

- **Linhas de Código:** ~8.000+ (Python)
- **Testes:** 427 (99% cobertura)
- **Endpoints:** 49
- **Models:** 9
- **Serializers:** 14
- **ViewSets:** 12

---

## 🔄 Changelog

### v4.0.0 (2026-03-17)
- ✨ Endpoints de configurações da conta (`/account/` e `/change-password/`)
- ✨ `UserAccountSerializer` — atualização de email, phone e username com confirmação de senha
- ✨ `ChangePasswordSerializer` — alteração de senha com validações completas
- 🧪 Expandido testes de 414 para 427
- 📚 Atualizada documentação (v4.0, 49 endpoints)

### v3.0.0 (2026-03-16)
- ✨ Login com username, email ou telefone
- ✨ Campo `phone` no modelo User
- ✨ Remoção do modelo Comment (substituído por Replies)
- ✨ Persistência de likes com `is_liked` e `like_id`
- ✨ Correção do comportamento de retweets
- ✨ Filtros dinâmicos em `GET /api/posts/`
- ✨ Integração com Cloudinary
- ✨ Aumento dos limites de GIF (15MB) e profile_image (5MB)
- 🧪 414 testes
- 📚 47 endpoints

### v2.0.0 (2026-02-19)
- ✨ Retweets, Replies, Mídias, Polls, Geolocalização
- ✨ Posts Agendados, Views Counter, Hashtags, Notificações, Busca
- 🧪 404 testes

### v1.0.0 (2026-01-08)
- 🎉 Release inicial — Auth, CRUD, Follows, Curtidas, Feed
- 🧪 83 testes

---

## 🎓 Projeto Educacional & Portfólio

Desenvolvido como projeto final de curso e portfólio backend profissional demonstrando: Django & DRF avançado, Celery + Redis, testes automatizados, CI/CD, deploy em produção e arquitetura modular.

---

## 👨‍💻 Autor

**Victor Pires** — [@victorpiressk](https://github.com/victorpiressk) — [LinkedIn](https://www.linkedin.com/in/victor-p-rego/)

---

**Versão:** 4.0.0  
**Última atualização:** 17/03/2026  
**Status:** ✅ Em Produção