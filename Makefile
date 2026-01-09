# ==============================================
# Twitter Clone API - Makefile (Development)
# ==============================================

.PHONY: help

# Variáveis
COMPOSE = docker-compose
API_SERVICE = backend
DB_SERVICE = db

##@ Help
help: ## Mostra todos os comandos disponíveis
	@echo "=========================================="
	@echo "Twitter Clone API - Comandos Disponíveis"
	@echo "=========================================="
	@echo ""
	@echo "Docker:"
	@echo "  make build           - Build das imagens Docker"
	@echo "  make up              - Inicia os containers"
	@echo "  make down            - Para os containers"
	@echo "  make restart         - Reinicia os containers"
	@echo "  make logs            - Mostra logs de todos os containers"
	@echo "  make logs-api        - Mostra logs apenas da API"
	@echo "  make logs-db         - Mostra logs apenas do banco"
	@echo "  make status          - Mostra status dos containers"
	@echo ""
	@echo "Acesso aos Containers:"
	@echo "  make shell           - Acessa shell do container da API"
	@echo "  make shell-db        - Acessa shell do PostgreSQL"
	@echo ""
	@echo "Django/Database:"
	@echo "  make migrate         - Executa migrations"
	@echo "  make makemigrations  - Cria novas migrations"
	@echo "  make createsuperuser - Cria superusuário"
	@echo "  make showmigrations  - Mostra status das migrations"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format          - Formata código com Black"
	@echo "  make format-check    - Verifica formatação (sem alterar)"
	@echo "  make format-imports  - Organiza imports com isort"
	@echo "  make lint            - Verifica código com Flake8"
	@echo "  make check           - Roda format-check + lint"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Roda testes"
	@echo "  make test-cov        - Roda testes com cobertura"
	@echo "  make test-report     - Gera relatório HTML de testes"
	@echo ""
	@echo "Utilidades:"
	@echo "  make clean           - Remove containers e volumes"
	@echo "  make clean-all       - Remove tudo (containers, volumes, imagens)"
	@echo "  make backup-db       - Faz backup do banco de dados"
	@echo "  make restore-db      - Restaura backup do banco"
	@echo ""

##@ Docker
build: ## Build das imagens Docker
	@echo "🔨 Building Docker images..."
	$(COMPOSE) build

up: ## Inicia os containers
	@echo "🚀 Starting containers..."
	$(COMPOSE) up -d
	@echo "✅ Containers started!"
	@echo "📝 API: http://localhost:8000"
	@echo "🗄️  Database: localhost:5432"

down: ## Para os containers
	@echo "🛑 Stopping containers..."
	$(COMPOSE) down

restart: ## Reinicia os containers
	@echo "🔄 Restarting containers..."
	$(COMPOSE) restart

logs: ## Mostra logs de todos os containers
	$(COMPOSE) logs -f

logs-api: ## Mostra logs apenas da API
	$(COMPOSE) logs -f $(API_SERVICE)

logs-db: ## Mostra logs apenas do banco
	$(COMPOSE) logs -f $(DB_SERVICE)

status: ## Mostra status dos containers
	@echo "📊 Container status:"
	$(COMPOSE) ps

##@ Acesso aos Containers
shell: ## Acessa shell do container da API
	@echo "🐚 Accessing API container shell..."
	$(COMPOSE) exec $(API_SERVICE) /bin/bash

shell-db: ## Acessa shell do PostgreSQL
	@echo "🐘 Accessing PostgreSQL shell..."
	$(COMPOSE) exec $(DB_SERVICE) psql -U twitter_clone_api_dev -d twitter_clone_api_dev_db

##@ Django/Database
migrate: ## Executa migrations
	@echo "🔄 Running migrations..."
	$(COMPOSE) exec $(API_SERVICE) python manage.py migrate

makemigrations: ## Cria novas migrations
	@echo "📝 Creating migrations..."
	$(COMPOSE) exec $(API_SERVICE) python manage.py makemigrations

createsuperuser: ## Cria superusuário
	@echo "👤 Creating superuser..."
	$(COMPOSE) exec $(API_SERVICE) python manage.py createsuperuser

showmigrations: ## Mostra status das migrations
	@echo "📋 Migrations status:"
	$(COMPOSE) exec $(API_SERVICE) python manage.py showmigrations

##@ Code Quality
format: ## Formata código com Black
	@echo "✨ Formatting code with Black..."
	$(COMPOSE) exec $(API_SERVICE) black .
	@echo "✅ Code formatted!"

format-check: ## Verifica formatação sem alterar
	@echo "🔍 Checking code formatting..."
	$(COMPOSE) exec $(API_SERVICE) black --check .

format-imports: ## Organiza imports com isort
	@echo "📦 Organizing imports with isort..."
	$(COMPOSE) exec $(API_SERVICE) isort .
	@echo "✅ Imports organized!"

lint: ## Verifica código com Flake8
	@echo "🔍 Running Flake8 linter..."
	$(COMPOSE) exec $(API_SERVICE) flake8 .

check: format-check lint ## Roda todos os checks de qualidade
	@echo "✅ All code quality checks passed!"

##@ Testing
test: ## Roda testes
	@echo "🧪 Running tests..."
	$(COMPOSE) exec $(API_SERVICE) pytest

test-cov: ## Roda testes com cobertura
	@echo "🧪 Running tests with coverage..."
	$(COMPOSE) exec $(API_SERVICE) pytest --cov --cov-report=term-missing --cov-report=html

test-report: ## Gera relatório HTML de testes
	@echo "🧪 Running tests and generating HTML report..."
	$(COMPOSE) exec $(API_SERVICE) pytest --html=htmlcov/report.html --self-contained-html
	@echo "✅ Report generated at htmlcov/report.html"

##@ Utilidades
clean: ## Remove containers e volumes
	@echo "🧹 Cleaning up containers and volumes..."
	$(COMPOSE) down -v
	@echo "✅ Cleanup completed!"

clean-all: ## Remove tudo (containers, volumes, imagens)
	@echo "🧹 Cleaning up everything..."
	$(COMPOSE) down -v --rmi all
	@echo "✅ Complete cleanup done!"

backup-db: ## Faz backup do banco de dados
	@echo "💾 Creating database backup..."
	$(COMPOSE) exec -T $(DB_SERVICE) pg_dump -U twitter_clone_api_dev twitter_clone_api_dev_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

restore-db: ## Restaura backup do banco
	@echo "⚠️  Restoring database backup..."
	@read -p "Enter backup file name: " backup_file; \
	$(COMPOSE) exec -T $(DB_SERVICE) psql -U twitter_clone_api_dev twitter_clone_api_dev_db < $$backup_file
	@echo "✅ Backup restored!"

##@ Workflows Completos
init: build up migrate createsuperuser ## Inicializa o projeto (primeira vez)
	@echo "✅ Project initialized!"
	@echo "📝 Access admin at: http://localhost:8000/admin"

update: down build up migrate ## Atualiza após git pull
	@echo "✅ Project updated!"

dev: format-imports format lint test ## Prepara código antes de commit
	@echo "✅ Code ready for commit!"
