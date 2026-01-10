# 🐳 Twitter Clone API - Docker

Guia para executar a API usando Docker (imagem pronta do Docker Hub).

---

## 🎯 Objetivo

Permitir que você rode a **Twitter Clone API** localmente usando apenas **Docker Desktop**.

**Não é necessário:**
- ❌ Clonar repositório
- ❌ Instalar Python/Poetry
- ❌ Configurar PostgreSQL manualmente
- ❌ Instalar dependências

**Apenas Docker Desktop!** 🎉

---

## 👨‍💻 Nota para Desenvolvedores

Se você deseja **contribuir com o projeto**, **modificar o código-fonte** ou **fazer o setup completo de desenvolvimento**:

👉 **Consulte o README principal:** [README.md](https://github.com/victorpiressk/twitter-clone-api#readme)

Lá você encontrará:
- Instruções para clonar o repositório
- Setup do ambiente de desenvolvimento local
- Guia de contribuição
- Estrutura completa do projeto

---

**Este documento foca apenas em executar a aplicação** usando a imagem pronta do Docker Hub para testes e estudos.

---

## 📋 Pré-requisitos

- **Docker Desktop** instalado ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose** (já vem incluído no Docker Desktop)

**Verificar instalação:**
```bash
docker --version
docker-compose --version
```

---

## 🐳 Docker Hub

**Imagem oficial:** https://hub.docker.com/r/victorpiressk/twitter-clone-api

**Versões disponíveis:**
- `latest` - Última versão estável
- `1.0.0` - Release inicial (Janeiro 2026)

---

## 🚀 Quick Start

### 1. Pull da imagem do Docker Hub
```bash
docker pull victorpiressk/twitter-clone-api:latest
```

---

### 2. Criar arquivo docker-compose.yml

Crie um arquivo `docker-compose.yml` no seu diretório:
```yaml
version: '3.9'

services:
  backend:
    image: victorpiressk/twitter-clone-api:latest
    container_name: twitter_clone_api
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    environment:
      - DEBUG=True
      - SECRET_KEY=dev-secret-key-change-in-production
      - ALLOWED_HOSTS=localhost,127.0.0.1,[::1]
      - SQL_ENGINE=django.db.backends.postgresql
      - SQL_DATABASE=twitter_clone_api_dev_db
      - SQL_USER=twitter_clone_api_dev
      - SQL_PASSWORD=twitter_clone_api_dev
      - SQL_HOST=db
      - SQL_PORT=5432
      - CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
    depends_on:
      db:
        condition: service_healthy
    networks:
      - twitter_network

  db:
    image: postgres:14.0-alpine
    container_name: twitter_clone_db
    environment:
      - POSTGRES_DB=twitter_clone_api_dev_db
      - POSTGRES_USER=twitter_clone_api_dev
      - POSTGRES_PASSWORD=twitter_clone_api_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U twitter_clone_api_dev -d twitter_clone_api_dev_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - twitter_network

volumes:
  postgres_data:

networks:
  twitter_network:
    driver: bridge
```

---

### 3. Subir os containers
```bash
docker-compose up -d
```

---

### 4. Executar migrations
```bash
docker-compose exec backend python manage.py migrate
```

---

### 5. Criar superusuário (opcional)
```bash
docker-compose exec backend python manage.py createsuperuser
```

Siga as instruções no terminal:
- Username: `admin` (ou o que preferir)
- Email: `admin@example.com`
- Password: `sua_senha_segura`

---

### 6. Acessar a aplicação

- **API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/
- **Usuários:** http://localhost:8000/api/users/
- **Posts:** http://localhost:8000/api/posts/

---

## 📝 Comandos Úteis

### Gerenciamento de Containers
```bash
# Ver status dos containers
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Ver logs apenas da API
docker-compose logs -f backend

# Ver logs apenas do banco
docker-compose logs -f db

# Parar containers
docker-compose down

# Parar e remover volumes (apaga dados do banco!)
docker-compose down -v

# Reiniciar containers
docker-compose restart

# Reiniciar apenas a API
docker-compose restart backend
```

---

### Django Management
```bash
# Acessar shell do Django
docker-compose exec backend python manage.py shell

# Ver status das migrations
docker-compose exec backend python manage.py showmigrations

# Criar migrations (se modificou models)
docker-compose exec backend python manage.py makemigrations

# Executar migrations
docker-compose exec backend python manage.py migrate

# Listar todos os usuários
docker-compose exec backend python manage.py shell -c "from users.models import User; print(User.objects.all())"
```

---

### Acesso aos Containers
```bash
# Entrar no shell do container da API
docker-compose exec backend /bin/bash

# Entrar no PostgreSQL
docker-compose exec db psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db

# Listar bancos de dados
docker-compose exec db psql -U twitter_clone_api_dev -c "\l"
```

---

### Testes
```bash
# Rodar todos os testes
docker-compose exec backend pytest

# Testes com cobertura
docker-compose exec backend pytest --cov --cov-report=term-missing

# Rodar teste específico
docker-compose exec backend pytest users/tests/test_models.py
```

---

## 🔐 Variáveis de Ambiente

As variáveis de ambiente estão configuradas diretamente no `docker-compose.yml`.

**Variáveis principais:**

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `DEBUG` | `True` | Modo debug (dev only) |
| `SECRET_KEY` | `dev-secret-key...` | Chave secreta Django |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts permitidos |
| `SQL_DATABASE` | `twitter_clone_api_dev_db` | Nome do banco |
| `SQL_USER` | `twitter_clone_api_dev` | Usuário do PostgreSQL |
| `SQL_PASSWORD` | `twitter_clone_api_dev` | Senha do PostgreSQL |
| `SQL_HOST` | `db` | Host do banco (nome do serviço) |
| `SQL_PORT` | `5432` | Porta do PostgreSQL |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000` | Origens CORS permitidas |

**Para alterar:** Edite o arquivo `docker-compose.yml` antes de subir os containers.

---

## 📦 Estrutura dos Containers

### Container: backend (API)
- **Imagem:** `victorpiressk/twitter-clone-api:latest`
- **Porta:** 8000
- **Comando:** `python manage.py runserver 0.0.0.0:8000`
- **Rede:** `twitter_network`

### Container: db (PostgreSQL)
- **Imagem:** `postgres:14.0-alpine`
- **Porta:** 5432
- **Volume:** `postgres_data` (persistente)
- **Rede:** `twitter_network`

---

## 🔍 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker-compose logs backend

# Verificar status
docker-compose ps

# Remover tudo e começar do zero
docker-compose down -v
docker-compose up -d
```

---

### Erro de conexão com banco
```bash
# Verificar se banco está rodando
docker-compose ps db

# Ver logs do banco
docker-compose logs db

# Verificar saúde do banco
docker-compose exec db pg_isready -U twitter_clone_api_dev

# Reiniciar banco
docker-compose restart db
```

---

### Erro nas migrations
```bash
# Ver status
docker-compose exec backend python manage.py showmigrations

# Rodar migrations manualmente
docker-compose exec backend python manage.py migrate

# Se falhar, recrie o banco
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

---

### Porta 8000 já está em uso
```bash
# Ver o que está usando a porta
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Mudar a porta no docker-compose.yml
# Troque "8000:8000" por "8001:8000"
# Acesse: http://localhost:8001
```

---

### Container reiniciando constantemente
```bash
# Ver logs para identificar erro
docker-compose logs -f backend

# Possíveis causas:
# - Banco não está pronto (aguarde ~30s)
# - Erro nas migrations
# - Variável de ambiente faltando
```

---

### Resetar tudo (factory reset)
```bash
# Para todos os containers
docker-compose down -v

# Remove imagens (força download novamente)
docker rmi victorpiressk/twitter-clone-api:latest
docker rmi postgres:14.0-alpine

# Pull fresco
docker pull victorpiressk/twitter-clone-api:latest

# Reinicia
docker-compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

---

## 💾 Backup e Restore

### Backup do Banco de Dados
```bash
# Criar backup
docker-compose exec -T db pg_dump -U twitter_clone_api_dev twitter_clone_api_dev_db > backup.sql

# Verificar se foi criado
ls -lh backup.sql
```

**Windows PowerShell:**
```powershell
docker-compose exec -T db pg_dump -U twitter_clone_api_dev twitter_clone_api_dev_db | Out-File -Encoding utf8 backup.sql
```

---

### Restore do Banco de Dados
```bash
# Restaurar backup
docker-compose exec -T db psql -U twitter_clone_api_dev twitter_clone_api_dev_db < backup.sql
```

**Windows PowerShell:**
```powershell
Get-Content backup.sql | docker-compose exec -T db psql -U twitter_clone_api_dev twitter_clone_api_dev_db
```

---

## 📊 Monitoramento

### Ver uso de recursos
```bash
# Stats em tempo real
docker stats

# Apenas containers deste projeto
docker stats backend db
```

---

### Informações dos containers
```bash
# Inspecionar container
docker inspect backend

# Ver portas mapeadas
docker port backend

# Ver volumes
docker volume ls
docker volume inspect twitter_clone_postgres_data
```

---

## 🎯 Casos de Uso

### Caso 1: Testar a API rapidamente
```bash
# 1. Pull da imagem
docker pull victorpiressk/twitter-clone-api:latest

# 2. Criar docker-compose.yml (copie do Quick Start)

# 3. Subir
docker-compose up -d

# 4. Migrations
docker-compose exec backend python manage.py migrate

# 5. Testar
curl http://localhost:8000/api/users/
```

---

### Caso 2: Estudar o projeto
```bash
# 1. Rodar aplicação
docker-compose up -d

# 2. Criar superuser
docker-compose exec backend python manage.py createsuperuser

# 3. Explorar admin
# http://localhost:8000/admin

# 4. Criar dados de teste
docker-compose exec backend python manage.py shell
>>> from users.models import User
>>> User.objects.create_user(username='teste', email='teste@test.com', password='senha123')
```

---

### Caso 3: Integração com Frontend
```bash
# 1. Rodar a API
docker-compose up -d

# 2. API disponível em:
http://localhost:8000/api/

# 3. Frontend pode consumir:
# - Registro: POST /api/auth/register/
# - Login: POST /api/auth/login/
# - Posts: GET /api/posts/
# - etc
```

**Documentação completa da API:** [API_ENDPOINTS.md](https://github.com/victorpiressk/twitter-clone-api/blob/main/API_ENDPOINTS.md)

---

## ⚠️ Notas Importantes

### 🧪 Apenas para Desenvolvimento e Testes

Esta imagem Docker foi criada **exclusivamente para desenvolvimento local e testes**.

**Características da imagem atual:**
- ✅ Django `runserver` (não production-ready)
- ✅ `DEBUG=True` habilitado
- ✅ Sem otimizações de segurança
- ✅ Sem configurações de performance
- ✅ Configurações hardcoded para desenvolvimento

---

### 🚫 NÃO Utilize em Produção

**Para produção:**
- ❌ Não use esta imagem Docker
- ❌ Não use `docker-compose.yml` para deploy
- ✅ Faça deploy direto da aplicação Django
- ✅ Use Gunicorn como servidor WSGI
- ✅ Configure variáveis de ambiente na plataforma
- ✅ Use banco gerenciado (PostgreSQL)

**Plataformas recomendadas para produção:**
- Render
- Railway
- Fly.io
- Heroku

**Instruções de deploy:** [README.md - Seção Deploy](https://github.com/victorpiressk/twitter-clone-api#-deploy-em-produção)

---

### 🔐 Segurança

**Variáveis de ambiente padrão são inseguras!**

Se você for expor a API publicamente (mesmo que temporariamente):

1. **Mude o `SECRET_KEY`:**
```bash
# Gerar nova chave
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **Mude as senhas do banco:**
```yaml
SQL_PASSWORD=SuaSenhaMaisSegura123!
```

3. **Configure `ALLOWED_HOSTS` corretamente**

4. **Nunca use `DEBUG=True` em produção**

---

### 📌 Resumo

| Contexto | Usar esta imagem? | Como fazer? |
|----------|-------------------|-------------|
| **Testes locais** | ✅ SIM | Docker Compose |
| **Estudos** | ✅ SIM | Docker Compose |
| **Desenvolvimento** | ⚠️ Opcional | Melhor clonar repo |
| **Produção** | ❌ NÃO | Deploy direto (Gunicorn) |

---

## 📚 Recursos Adicionais

### Documentação
- [README Principal](https://github.com/victorpiressk/twitter-clone-api#readme)
- [Documentação da API](https://github.com/victorpiressk/twitter-clone-api/blob/main/API_ENDPOINTS.md)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Tecnologias Utilizadas
- [Django 6.0](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL 14](https://www.postgresql.org/docs/14/)
- [Poetry](https://python-poetry.org/)

### Suporte
- **Issues:** https://github.com/victorpiressk/twitter-clone-api/issues
- **Discussões:** https://github.com/victorpiressk/twitter-clone-api/discussions

---

## 🤝 Contribuindo

Quer contribuir com o projeto? 

👉 **Veja o guia completo:** [README.md - Seção Contribuindo](https://github.com/victorpiressk/twitter-clone-api#-contribuindo)

---

## 📝 Licença

Este projeto foi desenvolvido para fins educacionais.

---

## 👨‍💻 Autor

**Victor Pires**
- GitHub: [@victorpiressk](https://github.com/victorpiressk)
- Docker Hub: [@victorpiressk](https://hub.docker.com/u/victorpiressk)

---

**Última atualização:** Janeiro 2026  
**Versão da Imagem:** 1.0.0  
**Imagem Docker:** `victorpiressk/twitter-clone-api:latest`

---

⭐ **Se este projeto te ajudou, deixe uma estrela no GitHub!**

🐳 **Pull da imagem:** `docker pull victorpiressk/twitter-clone-api:latest`
