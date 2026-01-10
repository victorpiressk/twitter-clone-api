# API Endpoints - Twitter Clone

Documentação completa de todos os endpoints da API REST do Twitter Clone.

---

## 📋 Índice

- [Autenticação](#autenticação)
- [Usuários](#usuários)
- [Follows](#follows)
- [Posts](#posts)
- [Comentários](#comentários)
- [Curtidas](#curtidas)

---

## 🔐 Autenticação

Todos os endpoints protegidos requerem um token de autenticação no header:

```
Authorization: Token <seu_token_aqui>
```

---

### 1. Registrar Novo Usuário

**Endpoint:** `POST /api/auth/register/`

**Autenticação:** Não requerida

**Body:**
```json
{
  "username": "novouser",
  "email": "novo@example.com",
  "password": "senha12345",
  "password_confirm": "senha12345",
  "first_name": "Novo",
  "last_name": "Usuário"
}
```

**Resposta (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "novouser",
    "email": "novo@example.com",
    "first_name": "Novo",
    "last_name": "Usuário",
    "bio": "",
    "profile_image": null,
    "followers_count": 0,
    "following_count": 0,
    "posts_count": 0,
    "created_at": "2026-01-08T10:30:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Senhas não coincidem, username/email já existe, campos obrigatórios faltando

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Autenticação:** Não requerida

**Body:**
```json
{
  "username": "novouser",
  "password": "senha12345"
}
```

**Resposta (200 OK):**
```json
{
  "user": {
    "id": 1,
    "username": "novouser",
    "email": "novo@example.com",
    "first_name": "Novo",
    "last_name": "Usuário",
    "bio": "",
    "profile_image": null,
    "followers_count": 0,
    "following_count": 0,
    "posts_count": 0,
    "created_at": "2026-01-08T10:30:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Credenciais inválidas

---

### 3. Logout

**Endpoint:** `POST /api/auth/logout/`

**Autenticação:** Requerida

**Body:** Vazio

**Resposta (200 OK):**
```json
{
  "detail": "Logout realizado com sucesso."
}
```

**Erros Possíveis:**
- `401 Unauthorized` - Token inválido ou não fornecido

---

## 👥 Usuários

### 4. Listar Usuários

**Endpoint:** `GET /api/users/`

**Autenticação:** Não requerida

**Query Parameters:**
- `page` (opcional) - Número da página (padrão: 1)
- `page_size` (opcional) - Itens por página (padrão: 10)

**Resposta (200 OK):**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com",
      "first_name": "User",
      "last_name": "One",
      "bio": "Minha bio aqui",
      "profile_image": "http://localhost:8000/media/profile_images/user1.jpg",
      "followers_count": 150,
      "following_count": 200,
      "posts_count": 50,
      "created_at": "2026-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "username": "user2",
      "email": "user2@example.com",
      "first_name": "User",
      "last_name": "Two",
      "bio": "",
      "profile_image": null,
      "followers_count": 80,
      "following_count": 120,
      "posts_count": 30,
      "created_at": "2026-01-02T11:00:00Z"
    }
  ]
}
```

---

### 5. Detalhes de um Usuário

**Endpoint:** `GET /api/users/{id}/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "first_name": "User",
  "last_name": "One",
  "bio": "Minha bio aqui",
  "profile_image": "http://localhost:8000/media/profile_images/user1.jpg",
  "followers_count": 150,
  "following_count": 200,
  "posts_count": 50,
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `404 Not Found` - Usuário não existe

---

### 6. Usuário Autenticado (Me)

**Endpoint:** `GET /api/users/me/`

**Autenticação:** Requerida

**Resposta (200 OK):**
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "first_name": "User",
  "last_name": "One",
  "bio": "Minha bio aqui",
  "profile_image": "http://localhost:8000/media/profile_images/user1.jpg",
  "followers_count": 150,
  "following_count": 200,
  "posts_count": 50,
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `401 Unauthorized` - Não autenticado

---

### 7. Atualizar Perfil

**Endpoint:** `PATCH /api/users/{id}/`

**Autenticação:** Requerida (apenas o próprio usuário)

**Body (todos os campos opcionais):**
```json
{
  "bio": "Nova bio atualizada",
  "first_name": "Novo Nome",
  "profile_image": "<arquivo_base64_ou_upload>"
}
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "first_name": "Novo Nome",
  "last_name": "One",
  "bio": "Nova bio atualizada",
  "profile_image": "http://localhost:8000/media/profile_images/user1_new.jpg",
  "followers_count": 150,
  "following_count": 200,
  "posts_count": 50,
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Tentando editar perfil de outro usuário

---

### 8. Seguidores de um Usuário

**Endpoint:** `GET /api/users/{id}/followers/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
[
  {
    "id": 2,
    "username": "follower1",
    "email": "follower1@example.com",
    "first_name": "Follower",
    "last_name": "One",
    "bio": "",
    "profile_image": null,
    "followers_count": 50,
    "following_count": 100,
    "posts_count": 20,
    "created_at": "2026-01-02T10:00:00Z"
  },
  {
    "id": 3,
    "username": "follower2",
    "email": "follower2@example.com",
    "first_name": "Follower",
    "last_name": "Two",
    "bio": "",
    "profile_image": null,
    "followers_count": 30,
    "following_count": 80,
    "posts_count": 15,
    "created_at": "2026-01-03T10:00:00Z"
  }
]
```

---

### 9. Usuários que um Usuário Segue

**Endpoint:** `GET /api/users/{id}/following/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
[
  {
    "id": 4,
    "username": "following1",
    "email": "following1@example.com",
    "first_name": "Following",
    "last_name": "One",
    "bio": "Bio do usuário",
    "profile_image": null,
    "followers_count": 200,
    "following_count": 150,
    "posts_count": 80,
    "created_at": "2026-01-04T10:00:00Z"
  }
]
```

---

## 🤝 Follows

### 10. Listar Follows

**Endpoint:** `GET /api/follows/`

**Autenticação:** Requerida

**Resposta (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "follower": 1,
      "following": 2,
      "follower_username": "user1",
      "following_username": "user2",
      "created_at": "2026-01-05T10:00:00Z"
    }
  ]
}
```

---

### 11. Seguir um Usuário

**Endpoint:** `POST /api/follows/`

**Autenticação:** Requerida

**Body:**
```json
{
  "following": 2
}
```

**Resposta (201 Created):**
```json
{
  "id": 1,
  "follower": 1,
  "following": 2,
  "follower_username": "user1",
  "following_username": "user2",
  "created_at": "2026-01-05T10:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Já está seguindo esse usuário, ou tentando seguir a si mesmo
- `401 Unauthorized` - Não autenticado

---

### 12. Deixar de Seguir

**Endpoint:** `DELETE /api/follows/{id}/`

**Autenticação:** Requerida (apenas quem criou o follow)

**Resposta (204 No Content):**
Sem body

**Erros Possíveis:**
- `403 Forbidden` - Tentando deletar follow de outro usuário
- `404 Not Found` - Follow não existe

---

## 📝 Posts

### 13. Listar Posts

**Endpoint:** `GET /api/posts/`

**Autenticação:** Não requerida

**Query Parameters:**
- `page` (opcional) - Número da página
- `page_size` (opcional) - Itens por página

**Resposta (200 OK):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "author": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "User",
        "last_name": "One",
        "bio": "Minha bio",
        "profile_image": null,
        "followers_count": 150,
        "following_count": 200,
        "posts_count": 50,
        "created_at": "2026-01-01T10:00:00Z"
      },
      "content": "Este é o conteúdo do meu primeiro post!",
      "image": null,
      "likes_count": 25,
      "comments_count": 10,
      "created_at": "2026-01-08T14:30:00Z",
      "updated_at": "2026-01-08T14:30:00Z"
    }
  ]
}
```

---

### 14. Detalhes de um Post

**Endpoint:** `GET /api/posts/{id}/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "id": 1,
  "author": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "User",
    "last_name": "One",
    "bio": "Minha bio",
    "profile_image": null,
    "followers_count": 150,
    "following_count": 200,
    "posts_count": 50,
    "created_at": "2026-01-01T10:00:00Z"
  },
  "content": "Este é o conteúdo do meu primeiro post!",
  "image": "http://localhost:8000/media/post_images/post1.jpg",
  "likes_count": 25,
  "comments_count": 10,
  "created_at": "2026-01-08T14:30:00Z",
  "updated_at": "2026-01-08T14:30:00Z"
}
```

---

### 15. Criar Post

**Endpoint:** `POST /api/posts/`

**Autenticação:** Requerida

**Body:**
```json
{
  "content": "Meu novo post incrível!",
  "image": "<arquivo_opcional>"
}
```

**Resposta (201 Created):**
```json
{
  "id": 2,
  "author": {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com",
    "first_name": "User",
    "last_name": "One",
    "bio": "Minha bio",
    "profile_image": null,
    "followers_count": 150,
    "following_count": 200,
    "posts_count": 51,
    "created_at": "2026-01-01T10:00:00Z"
  },
  "content": "Meu novo post incrível!",
  "image": null,
  "likes_count": 0,
  "comments_count": 0,
  "created_at": "2026-01-08T15:00:00Z",
  "updated_at": "2026-01-08T15:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Conteúdo vazio ou excede 280 caracteres
- `401 Unauthorized` - Não autenticado

---

### 16. Atualizar Post

**Endpoint:** `PATCH /api/posts/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Body:**
```json
{
  "content": "Conteúdo atualizado"
}
```

**Resposta (200 OK):**
```json
{
  "id": 2,
  "author": {...},
  "content": "Conteúdo atualizado",
  "image": null,
  "likes_count": 0,
  "comments_count": 0,
  "created_at": "2026-01-08T15:00:00Z",
  "updated_at": "2026-01-08T15:30:00Z"
}
```

**Erros Possíveis:**
- `403 Forbidden` - Tentando editar post de outro usuário
- `404 Not Found` - Post não existe

---

### 17. Deletar Post

**Endpoint:** `DELETE /api/posts/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Resposta (204 No Content):**
Sem body

**Erros Possíveis:**
- `403 Forbidden` - Tentando deletar post de outro usuário
- `404 Not Found` - Post não existe

---

### 18. Feed Personalizado

**Endpoint:** `GET /api/posts/feed/`

**Autenticação:** Requerida

**Descrição:** Retorna posts dos usuários que você segue + seus próprios posts

**Resposta (200 OK):**
```json
[
  {
    "id": 5,
    "author": {
      "id": 2,
      "username": "following1",
      "email": "following1@example.com",
      "first_name": "Following",
      "last_name": "One",
      "bio": "",
      "profile_image": null,
      "followers_count": 100,
      "following_count": 50,
      "posts_count": 30,
      "created_at": "2026-01-02T10:00:00Z"
    },
    "content": "Post de alguém que eu sigo",
    "image": null,
    "likes_count": 15,
    "comments_count": 5,
    "created_at": "2026-01-08T16:00:00Z",
    "updated_at": "2026-01-08T16:00:00Z"
  },
  {
    "id": 2,
    "author": {
      "id": 1,
      "username": "user1",
      ...
    },
    "content": "Meu próprio post",
    "image": null,
    "likes_count": 10,
    "comments_count": 3,
    "created_at": "2026-01-08T15:00:00Z",
    "updated_at": "2026-01-08T15:00:00Z"
  }
]
```

---

## 💬 Comentários

### 19. Listar Comentários

**Endpoint:** `GET /api/comments/`

**Autenticação:** Não requerida

**Query Parameters:**
- `post` (opcional) - Filtrar por ID do post

**Resposta (200 OK):**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "commenter",
        "email": "commenter@example.com",
        "first_name": "Comment",
        "last_name": "User",
        "bio": "",
        "profile_image": null,
        "followers_count": 20,
        "following_count": 30,
        "posts_count": 10,
        "created_at": "2026-01-03T10:00:00Z"
      },
      "post": 1,
      "content": "Ótimo post!",
      "created_at": "2026-01-08T16:30:00Z",
      "updated_at": "2026-01-08T16:30:00Z"
    }
  ]
}
```

---

### 20. Criar Comentário

**Endpoint:** `POST /api/comments/`

**Autenticação:** Requerida

**Body:**
```json
{
  "post": 1,
  "content": "Meu comentário aqui"
}
```

**Resposta (201 Created):**
```json
{
  "id": 2,
  "user": {
    "id": 1,
    "username": "user1",
    ...
  },
  "post": 1,
  "content": "Meu comentário aqui",
  "created_at": "2026-01-08T17:00:00Z",
  "updated_at": "2026-01-08T17:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Conteúdo vazio ou post não existe
- `401 Unauthorized` - Não autenticado

---

### 21. Atualizar Comentário

**Endpoint:** `PATCH /api/comments/{id}/`

**Autenticação:** Requerida (apenas o autor do comentário)

**Body:**
```json
{
  "content": "Comentário atualizado"
}
```

**Resposta (200 OK):**
```json
{
  "id": 2,
  "user": {...},
  "post": 1,
  "content": "Comentário atualizado",
  "created_at": "2026-01-08T17:00:00Z",
  "updated_at": "2026-01-08T17:30:00Z"
}
```

---

### 22. Deletar Comentário

**Endpoint:** `DELETE /api/comments/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Resposta (204 No Content):**
Sem body

**Erros Possíveis:**
- `403 Forbidden` - Tentando deletar comentário de outro usuário

---

## ❤️ Curtidas

### 23. Listar Curtidas

**Endpoint:** `GET /api/likes/`

**Autenticação:** Não requerida

**Query Parameters:**
- `post` (opcional) - Filtrar por ID do post

**Resposta (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 2,
      "post": 1,
      "user_username": "liker1",
      "created_at": "2026-01-08T18:00:00Z"
    },
    {
      "id": 2,
      "user": 3,
      "post": 1,
      "user_username": "liker2",
      "created_at": "2026-01-08T18:15:00Z"
    }
  ]
}
```

---

### 24. Curtir um Post

**Endpoint:** `POST /api/likes/`

**Autenticação:** Requerida

**Body:**
```json
{
  "post": 1
}
```

**Resposta (201 Created):**
```json
{
  "id": 3,
  "user": 1,
  "post": 1,
  "user_username": "user1",
  "created_at": "2026-01-08T18:30:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Já curtiu este post
- `401 Unauthorized` - Não autenticado

---

### 25. Descurtir um Post

**Endpoint:** `DELETE /api/likes/{id}/`

**Autenticação:** Requerida (apenas quem curtiu)

**Resposta (204 No Content):**
Sem body

**Erros Possíveis:**
- `403 Forbidden` - Tentando deletar curtida de outro usuário
- `404 Not Found` - Curtida não existe

---

## 📊 Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 204 | No Content - Sucesso sem corpo de resposta |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Autenticação necessária |
| 403 | Forbidden - Sem permissão para esta ação |
| 404 | Not Found - Recurso não encontrado |
| 500 | Internal Server Error - Erro no servidor |

---

## 🔧 Testando a API

### Usando cURL:

```bash
# Registrar
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"pass123","password_confirm":"pass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"pass123"}'

# Criar Post (com token)
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -d '{"content":"Meu primeiro post!"}'
```

### Usando Python (requests):

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Registrar
response = requests.post(f"{BASE_URL}/auth/register/", json={
    "username": "testuser",
    "email": "test@test.com",
    "password": "pass123",
    "password_confirm": "pass123"
})
token = response.json()['token']

# Criar Post
headers = {"Authorization": f"Token {token}"}
response = requests.post(f"{BASE_URL}/posts/", 
    headers=headers,
    json={"content": "Meu primeiro post!"}
)
print(response.json())
```

### Usando JavaScript (Axios):

```javascript
import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api';

// Registrar
const registerResponse = await axios.post(`${BASE_URL}/auth/register/`, {
  username: 'testuser',
  email: 'test@test.com',
  password: 'pass123',
  password_confirm: 'pass123'
});

const token = registerResponse.data.token;

// Criar Post
const postResponse = await axios.post(
  `${BASE_URL}/posts/`,
  { content: 'Meu primeiro post!' },
  { headers: { Authorization: `Token ${token}` } }
);

console.log(postResponse.data);
```

---

## 📝 Notas Importantes

1. **Paginação:** Endpoints de listagem usam paginação padrão de 10 itens por página
2. **CORS:** A API está configurada para aceitar requests de `http://localhost:3000`
3. **Upload de Imagens:** Use `multipart/form-data` para enviar imagens
4. **Tokens:** Tokens não expiram automaticamente (implementação simples)
5. **Limites de Caracteres:**
   - Post: 280 caracteres
   - Comentário: 280 caracteres
   - Bio: 160 caracteres

---

## 🚀 Próximos Passos

- Implementar refresh tokens (JWT)
- Adicionar notificações em tempo real (WebSockets)
- Implementar busca de usuários e posts
- Adicionar hashtags
- Implementar retweets
- Adicionar mensagens diretas

---

**Documentação criada em:** 08/01/2026
**Versão da API:** 1.0
**Base URL (desenvolvimento):** `http://localhost:8000/api`
