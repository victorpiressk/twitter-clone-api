FROM python:3.14.0-slim

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=2.1.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Adicionar Poetry e venv ao PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Instalar dependências do sistema
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copiar e instalar dependências Python
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --sync

# Instalar explicitamente as dependências de dev
RUN poetry run pip install \
    pytest-django==4.11.1 \
    pytest-cov==7.0.0 \
    black==25.12.0 \
    flake8==7.3.0 \
    isort==7.0.0

# Copiar código da aplicação
WORKDIR /app
COPY . /app/

# Expor porta
EXPOSE 8000

# Comando para desenvolvimento (runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]