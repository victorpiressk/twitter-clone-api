# 🐳 Twitter Clone API - Guia Docker Completo

Documentação completa para desenvolvimento local usando Docker com todos os serviços necessários (Django, PostgreSQL, Redis, Celery).

---

## 🎯 Objetivo

Este guia cobre o **ambiente de desenvolvimento completo** usando Docker Compose, incluindo:

- ✅ **Django API** (backend)
- ✅ **PostgreSQL 14** (banco de dados)
- ✅ **Redis 7** (cache e broker)
- ✅ **Celery Worker** (processamento assíncrono)
- ✅ **Celery Beat** (agendador de tasks)

**Ideal para:**
- Desenvolvimento local em qualquer SO (Windows, macOS, Linux)
- Testes de funcionalidades assíncronas (posts agendados, notificações)
- Ambiente consistente entre desenvolvedores
- Não precisa instalar Python, PostgreSQL ou Redis localmente

---

## 📋 Pré-requisitos

- **Docker Desktop** instalado ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (incluído no Docker Desktop)
- **Git** (para clonar o repositório)

**Verificar instalação:**
```bash
docker --version        # Docker version 20.10.0+
docker-compose --version # Docker Compose version 1.29.0+
```

---

## 🚀 Quick Start

### 1. Clonar o Repositório

```bash
git clone https://github.com/victorpiressk/twitter-clone-api.git
cd twitter-clone-api
```

### 2. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env se necessário (valores padrão já funcionam)
```

### 3. Build e Iniciar Todos os Serviços

```bash
# Build das imagens e start dos containers
docker-compose up -d --build
```

**Aguarde ~30 segundos** para todos os serviços ficarem prontos.

### 4. Executar Migrations

```bash
docker-compose exec backend python manage.py migrate
```

### 5. Criar Superusuário

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 6. Acessar a Aplicação

- **API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/
- **Docs da API:** [API_ENDPOINTS.md](./API_ENDPOINTS.md)

**Pronto!** Todos os 5 serviços estão rodando. 🎉

---

## 📦 Arquitetura dos Serviços

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Network (backend)               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐    │
│  │  backend   │   │     db     │   │   redis    │    │
│  │  (Django)  │──▶│(PostgreSQL)│   │ (7-alpine) │    │
│  │  :8000     │   │  :5432     │   │   :6379    │    │
│  └────────────┘   └────────────┘   └─────┬──────┘    │
│         │                                  │           │
│         │          ┌──────────────────────┘           │
│         │          │                                   │
│  ┌──────▼──────────▼───┐   ┌────────────────────┐    │
│  │  celery_worker      │   │  celery_beat       │    │
│  │  (Tasks assíncronas)│   │  (Agendador)       │    │
│  │  --pool=solo        │   │  Schedule runner   │    │
│  └─────────────────────┘   └────────────────────┘    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 Serviços Detalhados

### 1. **backend** (Django API)

**Imagem:** Build local (Dockerfile)  
**Porta:** 8000  
**Comando:** `python manage.py runserver 0.0.0.0:8000`  
**Função:** Servir a API REST

**Features:**
- Hot reload (código atualiza automaticamente)
- Acesso ao shell Django
- Execução de migrations
- Testes

---

### 2. **db** (PostgreSQL)

**Imagem:** `postgres:14.0-alpine`  
**Porta:** 5432  
**Volume:** `postgres_data` (persistente)  
**Credenciais:**
- Database: `twitter_clone_api_dev_db`
- User: `twitter_clone_api_dev`
- Password: `twitter_clone_api_dev`

**Features:**
- Healthcheck configurado
- Dados persistem entre restarts
- Acesso direto via psql

---

### 3. **redis** (Cache & Message Broker)

**Imagem:** `redis:7-alpine` (versão 7.1.1)  
**Porta:** 6379  
**Função:** 
- Broker de mensagens para Celery
- Backend de resultados
- Cache (futuro)

**Features:**
- Healthcheck configurado
- Ping automático a cada 5s
- Restart automático em caso de falha

---

### 4. **celery_worker** (Processamento Assíncrono)

**Imagem:** Build local (Dockerfile)  
**Comando:** `celery -A config worker -l info --pool=solo`  
**Função:** Processar tasks assíncronas

**Tasks processadas:**
- Publicação de posts agendados
- Envio de notificações (futuro)
- Processamento de mídias (futuro)

**Nota:** `--pool=solo` é necessário para Windows (evita fork issues)

---

### 5. **celery_beat** (Agendador)

**Imagem:** Build local (Dockerfile)  
**Comando:** `celery -A config beat -l info`  
**Função:** Agendar tasks periódicas

**Schedule configurado:**
- A cada 1 minuto: verificar posts agendados para publicar
- Busca posts com `scheduled_for <= agora` e `is_published = False`

---

## 📝 Comandos Essenciais

### Gerenciamento de Containers

```bash
# Ver status de todos os serviços
docker-compose ps

# Ver logs em tempo real (todos os serviços)
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
docker-compose logs -f redis
docker-compose logs -f db

# Parar todos os serviços
docker-compose down

# Parar e remover volumes (⚠️ apaga banco de dados!)
docker-compose down -v

# Reiniciar todos os serviços
docker-compose restart

# Reiniciar serviço específico
docker-compose restart backend
docker-compose restart celery_worker

# Rebuild das imagens (após mudança no código)
docker-compose up -d --build
```

---

### Django Management

```bash
# Acessar shell do Django
docker-compose exec backend python manage.py shell

# Migrations
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py showmigrations

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic --noinput

# Shell do Python puro
docker-compose exec backend python

# Bash do container
docker-compose exec backend /bin/bash
```

---

### PostgreSQL

```bash
# Entrar no psql
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db

# Listar databases
docker-compose exec db psql -U twitter_clone_api_dev -c "\l"

# Listar tabelas
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db -c "\dt"

# Ver quantidade de posts
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db -c "SELECT COUNT(*) FROM posts_post;"

# Ver posts agendados
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db -c "SELECT id, content, scheduled_for, created_at FROM posts_post WHERE scheduled_for IS NOT NULL;"
```

---

### Redis

```bash
# Entrar no Redis CLI
docker-compose exec redis redis-cli

# Ping (verificar se está rodando)
docker-compose exec redis redis-cli ping
# Resposta esperada: PONG

# Ver quantidade de keys
docker-compose exec redis redis-cli DBSIZE

# Ver todas as keys
docker-compose exec redis redis-cli KEYS "*"

# Flush all (⚠️ limpa tudo)
docker-compose exec redis redis-cli FLUSHALL

# Ver info
docker-compose exec redis redis-cli INFO

# Ver tasks na fila (Celery)
docker-compose exec redis redis-cli LLEN celery

# Monitorar comandos em tempo real
docker-compose exec redis redis-cli MONITOR
```

---

### Celery

```bash
# Ver workers ativos
docker-compose exec backend celery -A config inspect active

# Ver tasks registradas
docker-compose exec backend celery -A config inspect registered

# Ver estatísticas
docker-compose exec backend celery -A config inspect stats

# Ver tasks agendadas (beat)
docker-compose exec backend celery -A config inspect scheduled

# Ver workers conectados
docker-compose exec backend celery -A config inspect ping

# Purgar todas as tasks da fila (⚠️ cuidado!)
docker-compose exec backend celery -A config purge

# Ver eventos em tempo real
docker-compose exec backend celery -A config events
```

---

### Testes

```bash
# Rodar todos os testes
docker-compose exec backend pytest

# Testes com cobertura
docker-compose exec backend pytest --cov --cov-report=term-missing

# Testes com relatório HTML
docker-compose exec backend pytest --cov --cov-report=html
# Ver em: htmlcov/index.html

# Rodar teste específico
docker-compose exec backend pytest posts/tests/test_models/
docker-compose exec backend pytest posts/tests/test_views/test_poll_views.py

# Rodar com verbose
docker-compose exec backend pytest -v

# Parar no primeiro erro
docker-compose exec backend pytest -x
```

---

### Qualidade de Código

```bash
# Formatação (Black)
docker-compose exec backend black .

# Organizar imports (Isort)
docker-compose exec backend isort .

# Lint (Flake8)
docker-compose exec backend flake8 .

# Rodar tudo de uma vez
docker-compose exec backend black . && docker-compose exec backend isort . && docker-compose exec backend flake8 .
```

---

## 🔬 Casos de Uso Práticos

### Caso 1: Testar Posts Agendados (Fluxo Completo)

Este é o fluxo **real** para testar posts agendados com múltiplos terminais:

#### **Terminal 1: Monitorar Logs do Celery Beat**

```bash
docker-compose logs -f celery_beat
```

**O que você verá:**
```
celery_beat | [2026-02-19 15:00:00] Scheduler: Sending due task posts.tasks.publish_scheduled_posts
```

#### **Terminal 2: Monitorar Logs do Celery Worker**

```bash
docker-compose logs -f celery_worker
```

**O que você verá:**
```
celery_worker | [2026-02-19 15:00:01] Task posts.tasks.publish_scheduled_posts succeeded
celery_worker | Published 1 scheduled posts
```

#### **Terminal 3: Criar Usuário e Post Agendado**

```bash
# 1. Criar usuário via API
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@test.com",
    "password": "senha123",
    "password_confirm": "senha123"
  }'

# Copie o TOKEN retornado

# 2. Criar post agendado para daqui 2 minutos
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -d '{
    "content": "Post agendado para daqui 2 minutos!",
    "scheduled_for": "2026-02-19T15:02:00Z"
  }'
```

#### **Terminal 4: Verificar no Banco (Opcional)**

```bash
# Ver posts agendados no banco
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db \
  -c "SELECT id, content, scheduled_for, created_at FROM posts_post WHERE scheduled_for IS NOT NULL ORDER BY scheduled_for;"
```

#### **Aguardar e Observar:**

1. **Celery Beat** detecta o post agendado a cada minuto
2. Quando `scheduled_for` <= agora, **Celery Beat envia task**
3. **Celery Worker** processa e publica o post
4. Post fica visível em `GET /api/posts/`

**Verificar publicação:**
```bash
curl http://localhost:8000/api/posts/ | jq '.results[] | {id, content, is_published, scheduled_for}'
```

---

### Caso 2: Testar Notificações Automáticas

```bash
# Terminal 1: Monitorar notificações sendo criadas
docker-compose logs -f backend | grep "Notification created"

# Terminal 2: Criar ações que geram notificações

# 1. Login com usuário 1
TOKEN_USER1=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"senha123"}' | jq -r '.token')

# 2. Login com usuário 2
TOKEN_USER2=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user2","password":"senha123"}' | jq -r '.token')

# 3. User1 cria um post
POST_ID=$(curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN_USER1" \
  -d '{"content":"Post do user1"}' | jq -r '.id')

# 4. User2 curte o post (gera notificação para user1)
curl -X POST http://localhost:8000/api/likes/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN_USER2" \
  -d "{\"post\":$POST_ID}"

# 5. User1 verifica notificações
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Token $TOKEN_USER1" | jq '.results'
```

---

### Caso 3: Desenvolvimento de Nova Feature

```bash
# 1. Criar branch
git checkout -b feature/minha-feature

# 2. Fazer mudanças no código (Hot reload automático)

# 3. Rodar testes
docker-compose exec backend pytest

# 4. Verificar qualidade
docker-compose exec backend black .
docker-compose exec backend isort .
docker-compose exec backend flake8 .

# 5. Commit
git add .
git commit -m "feat: adiciona minha feature"

# 6. Push
git push origin feature/minha-feature
```

---

### Caso 4: Debug de Task Celery

```bash
# 1. Entrar no shell Django
docker-compose exec backend python manage.py shell

# 2. Importar e executar task manualmente
>>> from posts.tasks import publish_scheduled_posts
>>> result = publish_scheduled_posts.delay()
>>> result.get()  # Ver resultado
>>> result.status  # Ver status

# 3. Ver logs detalhados
docker-compose logs -f celery_worker
```

---

## 🔍 Troubleshooting

### ❌ Backend não inicia

**Sintoma:** Container `backend` reinicia constantemente

**Verificar:**
```bash
# Ver logs
docker-compose logs backend

# Possíveis causas:
# - Banco não está pronto (aguarde ~30s)
# - Erro nas migrations
# - Variável de ambiente faltando
# - Porta 8000 em uso
```

**Solução:**
```bash
# Reiniciar tudo
docker-compose down
docker-compose up -d

# Executar migrations
docker-compose exec backend python manage.py migrate
```

---

### ❌ Redis não conecta

**Sintoma:** Celery mostra erro: `redis.exceptions.ConnectionError`

**Verificar:**
```bash
# Redis está rodando?
docker-compose ps redis

# Healthcheck ok?
docker-compose exec redis redis-cli ping
# Deve retornar: PONG

# Ver logs
docker-compose logs redis
```

**Solução:**
```bash
# Reiniciar Redis
docker-compose restart redis

# Verificar configuração no .env
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
```

---

### ❌ Celery Worker não processa tasks

**Sintoma:** Tasks ficam na fila mas não executam

**Verificar:**
```bash
# Worker está rodando?
docker-compose ps celery_worker

# Ver logs
docker-compose logs celery_worker

# Ver workers conectados
docker-compose exec backend celery -A config inspect ping
```

**Solução:**
```bash
# Reiniciar worker
docker-compose restart celery_worker

# Ver tasks na fila
docker-compose exec redis redis-cli LLEN celery

# Purgar fila se necessário
docker-compose exec backend celery -A config purge
```

---

### ❌ Posts agendados não publicam

**Sintoma:** Post com `scheduled_for` no passado não publica

**Verificar:**
```bash
# Celery Beat está rodando?
docker-compose ps celery_beat

# Ver logs do Beat
docker-compose logs celery_beat

# Ver logs do Worker
docker-compose logs celery_worker

# Verificar post no banco
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db \
  -c "SELECT id, content, scheduled_for, created_at FROM posts_post WHERE scheduled_for IS NOT NULL;"
```

**Causas comuns:**
- Celery Beat não está rodando
- Timezone incorreto (scheduled_for no futuro)
- Task não está registrada

**Solução:**
```bash
# Reiniciar Beat
docker-compose restart celery_beat

# Executar task manualmente (debug)
docker-compose exec backend python manage.py shell
>>> from posts.tasks import publish_scheduled_posts
>>> publish_scheduled_posts()
```

---

### ❌ Erro nas Migrations

**Sintoma:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solução:**
```bash
# Ver status
docker-compose exec backend python manage.py showmigrations

# Rollback e refazer
docker-compose exec backend python manage.py migrate posts zero
docker-compose exec backend python manage.py migrate

# Se persistir, resetar banco (⚠️ apaga dados!)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

---

### ❌ Porta 8000 já em uso

**Sintoma:** `Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use`

**Verificar:**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

**Solução 1:** Matar processo usando a porta

```bash
# Windows
taskkill /PID <PID> /F

# Linux/Mac
kill -9 <PID>
```

**Solução 2:** Mudar porta no docker-compose.yml

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Acesse em http://localhost:8001
```

---

### ❌ Volumes com permissão negada (Linux)

**Sintoma:** `PermissionError: [Errno 13] Permission denied`

**Solução:**
```bash
# Dar permissão ao diretório
sudo chown -R $USER:$USER .

# Ou rodar com sudo (não recomendado)
sudo docker-compose up -d
```

---

### ❌ Build lento (Windows)

**Sintoma:** Build demora muito tempo

**Solução:**
```bash
# Usar BuildKit
set COMPOSE_DOCKER_CLI_BUILD=1
set DOCKER_BUILDKIT=1
docker-compose build

# Ou adicionar ao docker-compose.yml:
version: '3.9'
x-build: &build-config
  context: .
  dockerfile: Dockerfile
  cache_from:
    - victorpiressk/twitter-clone-api:latest
```

---

### 🧹 Reset Completo (Factory Reset)

Quando tudo der errado, resete tudo:

```bash
# 1. Parar tudo
docker-compose down -v

# 2. Remover imagens
docker-compose rm -f
docker rmi twitter-clone-api_backend
docker rmi twitter-clone-api_celery_worker
docker rmi twitter-clone-api_celery_beat

# 3. Limpar build cache
docker builder prune -a

# 4. Rebuild tudo
docker-compose build --no-cache

# 5. Subir
docker-compose up -d

# 6. Migrations
docker-compose exec backend python manage.py migrate

# 7. Criar superuser
docker-compose exec backend python manage.py createsuperuser
```

---

## 💾 Backup e Restore

### Backup Completo

```bash
# 1. Backup do banco
docker-compose exec -T db pg_dump -U twitter_clone_api_dev twitter_clone_api_dev_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Backup dos arquivos de mídia (se existirem)
docker cp twitter_clone_api:/app/media ./media_backup

# 3. Backup do código (git)
git add .
git commit -m "backup: $(date +%Y-%m-%d)"
git push
```

### Restore

```bash
# 1. Restore do banco
cat backup_20260219_150000.sql | docker-compose exec -T db psql -U twitter_clone_api_dev twitter_clone_api_dev_db

# 2. Restore dos arquivos
docker cp ./media_backup twitter_clone_api:/app/media

# 3. Reiniciar serviços
docker-compose restart
```

---

## 📊 Monitoramento

### Ver Recursos Utilizados

```bash
# Stats em tempo real
docker stats

# Apenas serviços deste projeto
docker stats backend db redis celery_worker celery_beat

# Ver uso de disco
docker system df

# Ver volumes
docker volume ls
docker volume inspect twitter-clone-api_postgres_data
```

### Logs Estruturados

```bash
# Salvar logs em arquivo
docker-compose logs > logs_$(date +%Y%m%d).txt

# Logs com timestamp
docker-compose logs -t

# Últimas 100 linhas
docker-compose logs --tail=100

# Seguir logs de múltiplos serviços
docker-compose logs -f backend celery_worker celery_beat
```

---

## ⚙️ Variáveis de Ambiente

As variáveis estão no arquivo `.env` (baseado em `.env.example`):

### Django

```env
DEBUG=True
SECRET_KEY=sua-chave-dev
ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
```

### Database

```env
SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=twitter_clone_api_dev_db
SQL_USER=twitter_clone_api_dev
SQL_PASSWORD=twitter_clone_api_dev
SQL_HOST=db
SQL_PORT=5432
```

### Redis & Celery

```env
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### CORS

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🎯 Comandos Makefile (Atalhos)

Se você tiver um `Makefile`, pode criar atalhos:

```makefile
.PHONY: up down restart logs shell migrate test clean

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend python manage.py shell

migrate:
	docker-compose exec backend python manage.py migrate

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	docker system prune -f
```

**Uso:**
```bash
make up
make logs
make test
make clean
```

---

## 🚫 O Que NÃO Fazer

### ❌ NÃO use em Produção

Este setup Docker é **APENAS para desenvolvimento**.

**Por quê?**
- Django `runserver` (não production-ready)
- `DEBUG=True` expõe informações sensíveis
- Sem SSL/HTTPS
- Sem otimizações de performance
- Senhas hardcoded

**Para produção:** Use deployment direto (Gunicorn) - ver [README.md](./README.md#-deploy-em-produção)

### ❌ NÃO commite .env

```bash
# .gitignore já inclui:
.env
.env.local
```

### ❌ NÃO exponha portas publicamente

```yaml
# ❌ NUNCA:
ports:
  - "0.0.0.0:5432:5432"  # Expõe PostgreSQL publicamente

# ✅ OK (localhost apenas):
ports:
  - "5432:5432"
```

---

## 📚 Recursos Adicionais

### Documentação Oficial

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Redis Documentation](https://redis.io/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/14/)

### Repositório

- [README Principal](./README.md)
- [Documentação da API](./API_ENDPOINTS.md)
- [Issues](https://github.com/victorpiressk/twitter-clone-api/issues)

---

## 🔄 Workflow Típico de Desenvolvimento

```bash
# 1. Manhã: Iniciar ambiente
docker-compose up -d
docker-compose logs -f &  # Background

# 2. Desenvolver (hot reload automático)
# Editar código...

# 3. Testar mudanças
docker-compose exec backend pytest posts/tests/

# 4. Ver no browser
# http://localhost:8000/api/posts/

# 5. Commit
git add .
git commit -m "feat: nova feature"

# 6. Fim do dia: Parar ambiente
docker-compose down
```

---

## 🎓 Dicas de Produtividade

### Alias Úteis (Bash/Zsh)

Adicione ao seu `.bashrc` ou `.zshrc`:

```bash
# Docker Compose
alias dc='docker-compose'
alias dcup='docker-compose up -d'
alias dcdown='docker-compose down'
alias dclogs='docker-compose logs -f'
alias dcps='docker-compose ps'

# Django
alias djshell='docker-compose exec backend python manage.py shell'
alias djmigrate='docker-compose exec backend python manage.py migrate'
alias djtest='docker-compose exec backend pytest'

# Celery
alias celeryworker='docker-compose logs -f celery_worker'
alias celerybeat='docker-compose logs -f celery_beat'
```

**Uso:**
```bash
dcup
dclogs
djshell
djtest
```

### VS Code Integration

Instale extensões:
- Docker
- Remote - Containers

Configure `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "/usr/local/bin/python",
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "black"
}
```

---

## 📌 Resumo de Comandos Rápidos

```bash
# Setup inicial
docker-compose up -d --build
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Desenvolvimento diário
docker-compose up -d
docker-compose logs -f
docker-compose exec backend pytest

# Debug
docker-compose exec backend python manage.py shell
docker-compose logs -f celery_worker
docker-compose exec redis redis-cli

# Cleanup
docker-compose down
docker-compose down -v  # Remove volumes
```

---

## 👨‍💻 Autor

**Victor Pires**
- GitHub: [@victorpiressk](https://github.com/victorpiressk)
- LinkedIn: [in/victor-p-rego](https://www.linkedin.com/in/victor-p-rego/)

---

## 🤝 Contribuindo

Veja o guia completo em [README.md - Contribuindo](./README.md#-contribuindo)

---

**Versão:** 2.0.0  
**Última atualização:** 19/02/2026  
**Docker Compose:** v3.9  
**Serviços:** 5 (backend, db, redis, celery_worker, celery_beat)

---

⭐ **Se este projeto te ajudou, deixe uma estrela no GitHub!**

🐳 **Happy Coding!**
