# 🐳 Docker Setup - Twitter Clone API

Documentação para rodar o projeto com Docker em **ambiente de desenvolvimento**.

---

## 🎯 Objetivo

Este setup Docker permite que desenvolvedores em **diferentes sistemas operacionais** (Windows, macOS, Linux) rodem o projeto localmente sem precisar configurar Python, PostgreSQL e dependências manualmente.

---

## 📋 Pré-requisitos

- **Docker Desktop** instalado ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (incluído no Docker Desktop)

---

## 🚀 Quick Start

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/twitter-clone-api.git
cd twitter-clone-api
```

### 2. Build da imagem Docker
```bash
docker-compose build
```

### 3. Subir os containers
```bash
docker-compose up -d
```

### 4. Rodar migrations
```bash
docker-compose exec backend python manage.py migrate
```

### 5. Criar superusuário
```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Acessar a aplicação

- **API:** http://localhost:8000
- **Admin:** http://localhost:8000/admin
- **API Endpoints:** http://localhost:8000/api/

---

## 📝 Comandos Docker Compose

### Gerenciamento de Containers
```bash
# Build das imagens
docker-compose build

# Subir containers (modo detached)
docker-compose up -d

# Parar containers
docker-compose down

# Ver logs de todos os containers
docker-compose logs -f

# Ver logs apenas da API
docker-compose logs -f backend

# Ver logs apenas do banco
docker-compose logs -f db

# Ver status dos containers
docker-compose ps

# Reiniciar containers
docker-compose restart
```

---

### Django Management
```bash
# Rodar migrations
docker-compose exec backend python manage.py migrate

# Criar migrations
docker-compose exec backend python manage.py makemigrations

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# Shell do Django
docker-compose exec backend python manage.py shell

# Ver status das migrations
docker-compose exec backend python manage.py showmigrations
```

---

### Acesso aos Containers
```bash
# Entrar no shell do container da API
docker-compose exec backend /bin/bash

# Entrar no PostgreSQL
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db
```

---

### Testes
```bash
# Rodar todos os testes
docker-compose exec backend pytest

# Testes com cobertura
docker-compose exec backend pytest --cov --cov-report=html

# Ver relatório de cobertura
# Abrir: htmlcov/index.html no navegador
```

---

### Code Quality
```bash
# Formatar código com Black
docker-compose exec backend black .

# Verificar formatação (sem alterar)
docker-compose exec backend black --check .

# Organizar imports
docker-compose exec backend isort .

# Verificar código com Flake8
docker-compose exec backend flake8 .
```

---

## 📦 Estrutura dos Containers

### API Container (backend)
- **Nome:** `backend`
- **Porta:** 8000
- **Imagem:** Python 3.14.0-slim + Poetry
- **Comando:** `python manage.py runserver 0.0.0.0:8000`
- **Volume:** Código mapeado para hot-reload

### Database Container (db)
- **Nome:** `db`
- **Porta:** 5432
- **Imagem:** PostgreSQL 14.0-alpine
- **Banco:** `twitter_clone_api_dev_db`
- **Usuário:** `twitter_clone_api_dev`
- **Volume persistente:** `postgres_data`

---

## 🔐 Variáveis de Ambiente

As variáveis estão no arquivo `.env.example`:
```env
# Django
DEBUG=True
SECRET_KEY=foo
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]

# Database (PostgreSQL)
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=twitter_clone_api_dev_db
SQL_USER=twitter_clone_api_dev
SQL_PASSWORD=twitter_clone_api_dev
SQL_HOST=db
SQL_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Importante:** 
- O projeto usa `SQL_*` para variáveis de banco (não `DB_*`)
- O `docker-compose.yml` lê direto do `.env.example`
- Para valores customizados, copie para `.env` e ajuste

---

## 🔄 Hot-Reload (Desenvolvimento)

O código está mapeado como volume no `docker-compose.yml`:
```yaml
volumes:
  - .:/app
```

**Isso significa:**
- ✅ Edite arquivos localmente
- ✅ Mudanças refletem automaticamente no container
- ✅ Django runserver detecta e recarrega

**Exceções (precisa rebuild):**
- Mudanças no `Dockerfile`
- Mudanças no `pyproject.toml` (dependências)

---

## 🔍 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs backend

# Verificar status
docker-compose ps

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

### Erro de conexão com banco
```bash
# Verificar se banco está rodando
docker-compose logs db

# Verificar saúde do banco
docker-compose exec db pg_isready

# Restart do banco
docker-compose restart db
```

---

### Erro nas migrations
```bash
# Ver status das migrations
docker-compose exec backend python manage.py showmigrations

# Rodar migrations manualmente
docker-compose exec backend python manage.py migrate

# Se precisar, criar migrations
docker-compose exec backend python manage.py makemigrations
```

---

### Limpar tudo e começar do zero
```bash
# Para containers e remove volumes
docker-compose down -v

# Remove também as imagens
docker-compose down -v --rmi all

# Rebuild completo
docker-compose build
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## 💾 Backup e Restore do Banco

### Backup
```bash
docker-compose exec -T db pg_dump -U twitter_clone_api_dev twitter_clone_api_dev_db > backup_$(date +%Y%m%d_%H%M%S).sql
```
> No Windows PowerShell, defina manualmente o nome do arquivo ou use Git Bash.

### Restore
```bash
docker-compose exec -T db psql -U twitter_clone_api_dev twitter_clone_api_dev_db < backup_20260109_120000.sql
```

---

## 📊 Monitoramento

### Ver uso de recursos
```bash
# Stats dos containers
docker stats

# Apenas backend
docker stats backend

# Apenas db
docker stats db
```

---

## 🎯 Workflow Típico

### Setup Inicial (primeira vez)
```bash
git clone <repo>
cd twitter-clone-api
docker-compose build
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
# Acessar http://localhost:8000/admin
```

---

### Desenvolvimento Diário
```bash
# Subir containers
docker-compose up -d

# Trabalhar normalmente (hot-reload ativo)
# Editar código localmente

# Ver logs se precisar
docker-compose logs -f backend

# Rodar testes
docker-compose exec backend pytest

# Parar no fim do dia
docker-compose down
```

---

### Após git pull (atualizações)
```bash
# Se mudou Dockerfile ou pyproject.toml
docker-compose build

# Se mudou models
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Restart
docker-compose restart
```

---

## 🛑 Parar e Limpar
```bash
# Parar containers (mantém volumes)
docker-compose down

# Parar e remover volumes (perde dados do banco!)
docker-compose down -v

# Parar, remover volumes E imagens
docker-compose down -v --rmi all
```

---

## ⚠️ Notas Importantes

### 🔄 Sobre Produção e Deploy

Este projeto foi containerizado exclusivamente para facilitar o desenvolvimento local em diferentes sistemas operacionais (Windows, macOS e Linux).

---

### 🧪 Ambiente de Desenvolvimento (Docker)

#### No contexto de desenvolvimento, o Docker é utilizado para:

- Padronizar o ambiente de execução
- Evitar instalação manual de dependências
- Facilitar onboarding de novos desenvolvedores
- Garantir consistência entre máquinas

#### Características do setup atual:

- Django rodando com ``runserver``
- ``DEBUG=True``
- Hot-reload ativado via volumes
- Variáveis de ambiente carregadas a partir de ``.env.example``
- PostgreSQL local em container
- Sem hardening de segurança

Este não é um setup adequado para produção.

---

### 🚀 Ambiente de Produção (Deploy)

Para produção, a aplicação não utiliza Docker Compose nem este setup de desenvolvimento.

#### O fluxo recomendado é:

- Deploy direto da aplicação Django
- Uso de um servidor WSGI/ASGI (ex: Gunicorn)
- Variáveis de ambiente configuradas diretamente na plataforma de deploy
- Banco de dados gerenciado pela infraestrutura da plataforma (ex: PostgreSQL gerenciado)

#### Exemplo de plataformas compatíveis:

- Render
- Railway
- Fly.io
- Heroku (ou similares)

#### Nesse cenário:

- O Docker pode ser usado apenas como imagem base de build
- O ``docker-compose.yml`` não é utilizado
- ``.env.example`` serve apenas como referência
- As variáveis sensíveis são definidas no painel da plataforma

---

### 🐳 Docker Hub (Distribuição da Imagem)

#### A imagem Docker deste projeto pode ser publicada no Docker Hub com fins de:

- Estudo
- Demonstração técnica
- Distribuição padronizada do ambiente

#### Essa imagem:

- Não é a mesma usada em produção
- Serve como referência de arquitetura
- Pode ser utilizada como base para outros projetos

---

### 📌 Resumo

| Contexto              | Uso                        |
| --------------------- | -------------------------- |
| Desenvolvimento local | Docker + Docker Compose    |
| Produção              | Deploy direto da aplicação |
| Variáveis sensíveis   | Definidas na plataforma    |
| Docker Hub            | Distribuição / estudo      |

---

## 📚 Recursos

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Documentation](https://docs.djangoproject.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Última atualização:** Janeiro 2026  
**Versão:** 1.0 (Development)  
**Sistema:** Cross-platform (Windows, macOS, Linux)