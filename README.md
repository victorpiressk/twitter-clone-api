# 🐦 Twitter Clone - Backend API

![Build Status](https://github.com/victorpiressk/twitter-clone-api/workflows/Backend%20CI/badge.svg)
![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)
![Coverage](https://img.shields.io/badge/coverage-99%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.14-blue)

API REST desenvolvida com Django e Django REST Framework para uma rede social completa inspirada no Twitter.

---

## 🚀 Tecnologias

- **Python 3.14**
- **Django 6.0**
- **Django REST Framework 3.15+**
- **Poetry** (gerenciamento de dependências)
- **PostgreSQL 14** (desenvolvimento e produção)
- **Token Authentication** (DRF)
- **Pytest / Pytest-Django** (83 testes, 99% cobertura)
- **Docker & Docker Compose** (desenvolvimento cross-platform)
- **Black, Isort, Flake8** (qualidade de código)
- **GitHub Actions** (CI/CD)
- **Render** (deploy em produção)

---

## 📋 Funcionalidades

- ✅ Autenticação com Token (registro, login, logout)
- ✅ Gerenciamento de usuários e perfis
- ✅ Sistema de posts (criar, editar, listar, deletar)
- ✅ Curtidas e comentários
- ✅ Sistema de seguir/seguidores
- ✅ Feed personalizado
- ✅ Upload de imagens (perfil e posts)
- ✅ Testes automatizados (83 testes)
- ✅ Pipeline de CI/CD com validação de qualidade

---

## 📂 Estrutura do Projeto
```
twitter-clone-api/
├── config/                 # Configurações do Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── authentication/         # Sistema de autenticação
│   ├── serializers/
│   ├── views/
│   ├── tests/
│   └── urls.py
├── users/                  # Usuários, perfis e follows
│   ├── models/            # User, Follow
│   ├── serializers/
│   ├── views/
│   ├── permissions/
│   ├── tests/
│   └── urls.py
├── posts/                  # Posts, comentários e curtidas
│   ├── models/            # Post, Comment, Like
│   ├── serializers/
│   ├── views/
│   ├── permissions/
│   ├── tests/
│   └── urls.py
├── .github/workflows/      # CI/CD (GitHub Actions)
│   ├── build.yml
│   └── code-review.yml
├── Dockerfile              # Imagem Docker (desenvolvimento)
├── docker-compose.yml      # Orquestração (desenvolvimento)
├── Makefile                # Comandos úteis
├── pyproject.toml          # Dependências Poetry
├── .env.example            # Template de variáveis de ambiente
├── API_ENDPOINTS.md        # Documentação detalhada da API
├── README_DOCKER.md        # Documentação do Docker
└── manage.py
```

---

## 🔧 Instalação Local (sem Docker)

### Pré-requisitos
- Python 3.14
- Poetry 2.1.4+
- PostgreSQL 14+ (opcional para desenvolvimento)

### Passos
```bash
# 1. Clone o repositório
git clone https://github.com/victorpiressk/twitter-clone-api.git
cd twitter-clone-api

# 2. Instale Poetry (se não tiver)
pip install poetry==2.1.4

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

# 8. Inicie o servidor
poetry run python manage.py runserver
```

**A API estará disponível em:** `http://localhost:8000`

---

## 🐳 Desenvolvimento com Docker (Recomendado)

Este projeto utiliza Docker **apenas para desenvolvimento local**, garantindo ambiente consistente entre diferentes sistemas operacionais (Windows, macOS, Linux).

### Quick Start
```bash
# 1. Build e iniciar containers
docker-compose up -d

# 2. Executar migrations
docker-compose exec backend python manage.py migrate

# 3. Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# 4. Acessar
# API: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### 📘 Documentação Completa do Docker

Para instruções detalhadas, comandos úteis e troubleshooting:

👉 **[README_DOCKER.md](./README_DOCKER.md)**

---

## 📡 Documentação da API

A documentação detalhada de **todos os 25 endpoints** da API está disponível em arquivo dedicado:

👉 **[API_ENDPOINTS.md](./API_ENDPOINTS.md)**

**Inclui:**
- Rotas e métodos HTTP
- Parâmetros e body
- Exemplos de request/response
- Códigos de status
- Exemplos em cURL, Python e JavaScript

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

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Produção

Em produção (Render), as variáveis devem ser configuradas diretamente no painel do provedor, **sem uso de arquivo `.env`**.

---

## 🚀 Deploy em Produção

O deploy da aplicação é feito **sem Docker**, utilizando execução direta do Django com Gunicorn.

### Render (Recomendado)

**1. Criar Web Service no Render**

**2. Configurar Build Command:**
```bash
poetry install --no-root && python manage.py collectstatic --noinput && python manage.py migrate
```

**3. Configurar Start Command:**
```bash
poetry run gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3
```

**4. Configurar Variáveis de Ambiente:**

No painel do Render, adicione:
- `DEBUG=False`
- `SECRET_KEY=<gerar-chave-segura>`
- `ALLOWED_HOSTS=seu-dominio.onrender.com`
- `SQL_ENGINE=django.db.backends.postgresql`
- `SQL_DATABASE=<nome-do-banco>`
- `SQL_USER=<usuario>`
- `SQL_PASSWORD=<senha>`
- `SQL_HOST=<host-do-render>`
- `SQL_PORT=5432`
- `CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app`

**5. Criar Banco PostgreSQL:**

No Render, crie um PostgreSQL database e conecte ao Web Service.

---

## 🧪 Testes

O projeto possui **83 testes automatizados** com **99% de cobertura**.
```bash
# Rodar todos os testes
poetry run pytest

# Testes com cobertura
poetry run pytest --cov --cov-report=html

# Ver relatório de cobertura
# Abrir: htmlcov/index.html
```

**Estrutura de testes:**
- Models: 21 testes
- Serializers: 19 testes
- Views/Endpoints: 43 testes

Os testes são executados **automaticamente no GitHub Actions** a cada push e pull request.

---

## 🔄 CI/CD

### GitHub Actions

O projeto possui pipeline de CI/CD automatizado com dois workflows:

#### **Build & Test (`build.yml`):**
- ✅ Validação de código (Black, Isort, Flake8)
- ✅ Execução de 83 testes com PostgreSQL
- ✅ Relatório de cobertura (99%)
- ✅ Build da imagem Docker para validação

#### **Code Review (`code-review.yml`):**
- ✅ Análise estática de código
- ✅ Verificação de formatação
- ✅ Organização de imports

**Os workflows são executados em:**
- Pushes para `main` e `develop`
- Pull requests para qualquer branch

---

## 🧹 Qualidade de Código
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

**Ou com Docker:**
```bash
docker-compose exec backend black .
docker-compose exec backend isort .
docker-compose exec backend flake8 .
```

Essas verificações também fazem parte do pipeline de CI.

---

## 🔐 Admin do Django

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

---

## 🔐 Autenticação

A API usa **Token Authentication** do Django REST Framework.

### Como usar:

#### 1. **Registro:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "novouser",
    "email": "user@example.com",
    "password": "senha123",
    "password_confirm": "senha123"
  }'
```

**Resposta:**
```json
{
  "user": {
    "id": 1,
    "username": "novouser",
    "email": "user@example.com",
    ...
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

**Resposta:**
```json
{
  "user": {...},
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
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

### User
```python
- username (unique)
- email (unique)
- first_name
- last_name
- bio (max 160 chars)
- profile_image (upload)
- created_at
- updated_at
```

### Post
```python
- author (ForeignKey → User)
- content (max 280 chars)
- image (optional upload)
- created_at
- updated_at
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
- unique_together: (user, post)
```

### Follow
```python
- follower (ForeignKey → User)
- following (ForeignKey → User)
- created_at
- unique_together: (follower, following)
```

---

## 🔗 Integração com Frontend

Este backend foi projetado para integração com aplicações frontend modernas.

**Stack recomendada:**
- React / Next.js / Vue
- TypeScript
- Axios / Fetch API
- TailwindCSS

**Comunicação:**
- REST API autenticada com Token
- CORS configurado

**Configurar CORS em produção:**

No `config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = os.environ.get(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000'
).split(',')
```

Adicione seu domínio frontend nas variáveis de ambiente.

---

## 📌 Observações Importantes

- ✅ Docker é utilizado **exclusivamente para desenvolvimento**
- ✅ Em produção, a aplicação roda **diretamente via Python + Gunicorn**
- ✅ O projeto segue **boas práticas** de versionamento, CI/CD e organização
- ✅ Ideal como **projeto final de curso** e **portfólio backend**
- ✅ Código 100% testado e com pipeline de qualidade

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
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário

---

## 📚 Recursos Adicionais

- [Documentação Django](https://docs.djangoproject.com/)
- [Documentação DRF](https://www.django-rest-framework.org/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!**

---

**Versão:** 1.0.0  
**Última atualização:** Janeiro 2026
