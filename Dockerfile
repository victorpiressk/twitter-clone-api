# Stage 1: Builder
FROM python:3.14.0-slim as builder

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==2.1.4

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Configurar Poetry para não criar virtualenv (já estamos em container)
RUN poetry config virtualenvs.create false

# Instalar dependências
RUN poetry install --no-dev --no-interaction --no-ansi


# Stage 2: Runtime
FROM python:3.14.0-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=config.settings

# Criar usuário não-root
RUN useradd -m -u 1000 django && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R django:django /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar dependências instaladas do builder
COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código da aplicação
COPY --chown=django:django . .

# Mudar para usuário não-root
USER django

# Coletar arquivos estáticos
RUN python manage.py collectstatic --noinput --clear

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/admin/', timeout=2)"

# Comando padrão
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
