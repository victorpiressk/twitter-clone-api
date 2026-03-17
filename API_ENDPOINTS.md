# API Endpoints - Twitter Clone

Documentação completa de todos os endpoints da API REST do Twitter Clone.

**Versão:** 4.0  
**Última atualização:** 17/03/2026  
**Base URL (desenvolvimento):** `http://localhost:8000/api`

---

## 📋 Índice

- [Autenticação](#autenticação)
- [Usuários](#usuários)
- [Follows](#follows)
- [Posts](#posts)
  - [CRUD Básico](#crud-básico-de-posts)
  - [Retweets](#retweets)
  - [Replies](#replies)
  - [Múltiplas Mídias](#múltiplas-mídias)
  - [Posts Agendados](#posts-agendados)
  - [Trending](#trending-posts-mais-vistos)
- [Polls (Enquetes)](#polls-enquetes)
- [Locations (Geolocalização)](#locations-geolocalização)
- [Hashtags](#hashtags)
- [Notificações](#notificações)
- [Busca](#busca)
- [Curtidas](#curtidas)
- [Configurações da Conta](#configurações-da-conta)
- [Códigos de Status](#códigos-de-status-http)
- [Testando a API](#testando-a-api)

---

## 🔐 Autenticação

Todos os endpoints protegidos requerem um token de autenticação no header:

```http
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
  "phone": "11999999999",
  "password": "senha12345",
  "password_confirm": "senha12345",
  "first_name": "Novo",
  "last_name": "Usuário",
  "birth_date": "1995-06-15"
}
```

**Nota:** `email` e `phone` são opcionais individualmente, mas pelo menos um dos dois deve ser fornecido. `birth_date` é obrigatório.

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
    "banner": null,
    "location": "",
    "website": "",
    "birth_date": "1995-06-15",
    "stats": {
      "posts": 0,
      "following": 0,
      "followers": 0
    },
    "created_at": "2026-02-19T10:30:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Senhas não coincidem, username/email/phone já existe, campos obrigatórios faltando, idade menor que 13 anos, data de nascimento no futuro, email e phone ausentes simultaneamente

---

### 2. Login

**Endpoint:** `POST /api/auth/login/`

**Autenticação:** Não requerida

**Body:**
```json
{
  "identifier": "nome_de_usuario, email ou telefone",
  "password": "senha12345"
}
```

**Nota:** O campo `identifier` aceita username, email ou telefone.

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
    "banner": null,
    "location": "",
    "website": "",
    "birth_date": "1995-06-15",
    "stats": {
      "posts": 0,
      "following": 0,
      "followers": 0
    },
    "created_at": "2026-02-19T10:30:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Credenciais inválidas, identifier ou senha ausentes

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
      "bio": "Desenvolvedor Python 🐍",
      "profile_image": "https://res.cloudinary.com/seu_cloud/image/upload/profile_images/user1.jpg",
      "banner": "https://res.cloudinary.com/seu_cloud/image/upload/banners/user1_banner.jpg",
      "location": "São Paulo, Brasil",
      "website": "https://user1.dev",
      "birth_date": "1990-05-15",
      "stats": {
        "posts": 150,
        "following": 200,
        "followers": 350
      },
      "created_at": "2026-01-01T10:00:00Z"
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
  "bio": "Desenvolvedor Python 🐍",
  "profile_image": "https://res.cloudinary.com/seu_cloud/image/upload/profile_images/user1.jpg",
  "banner": "https://res.cloudinary.com/seu_cloud/image/upload/banners/user1_banner.jpg",
  "location": "São Paulo, Brasil",
  "website": "https://user1.dev",
  "birth_date": "1990-05-15",
  "stats": {
    "posts": 150,
    "following": 200,
    "followers": 350
  },
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `404 Not Found` - Usuário não existe

---

### 6. Usuário Autenticado (Me)

**Endpoint:** `GET /api/users/me/`

**Autenticação:** Requerida

**Resposta (200 OK):** Mesma estrutura do endpoint de detalhes.

**Erros Possíveis:**
- `401 Unauthorized` - Não autenticado

---

### 7. Atualizar Perfil

**Endpoint:** `PATCH /api/users/{id}/`

**Autenticação:** Requerida (apenas o próprio usuário)

**Content-Type:** `multipart/form-data` (para upload de imagens)

**Body (todos os campos opcionais):**
```json
{
  "bio": "Nova bio atualizada 🚀",
  "first_name": "Novo Nome",
  "location": "Rio de Janeiro, Brasil",
  "website": "https://novosite.com",
  "birth_date": "1995-10-20",
  "profile_image": "<arquivo>",
  "banner": "<arquivo>"
}
```

**Validações:**
- `bio`: máximo 160 caracteres
- `profile_image`: máximo 5MB, formatos: JPEG, PNG, WEBP
- `banner`: máximo 5MB, formatos: JPEG, PNG, WEBP
- `website`: deve começar com http:// ou https://
- `birth_date`: idade mínima 13 anos, não pode ser futura

**Erros Possíveis:**
- `400 Bad Request` - Validação falhou
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Tentando editar perfil de outro usuário

---

### 8. Seguidores de um Usuário

**Endpoint:** `GET /api/users/{id}/followers/`

**Autenticação:** Não requerida

---

### 9. Usuários que um Usuário Segue

**Endpoint:** `GET /api/users/{id}/following/`

**Autenticação:** Não requerida

---

## 🤝 Follows

### 10. Listar Follows

**Endpoint:** `GET /api/follows/`

**Autenticação:** Requerida

---

### 11. Seguir um Usuário

**Endpoint:** `POST /api/follows/`

**Autenticação:** Requerida

**Body:**
```json
{ "following": 2 }
```

**Erros Possíveis:**
- `400 Bad Request` - Já está seguindo esse usuário, ou tentando seguir a si mesmo
- `401 Unauthorized` - Não autenticado

---

### 12. Deixar de Seguir

**Endpoint:** `DELETE /api/follows/{id}/`

**Autenticação:** Requerida (apenas quem criou o follow)

**Resposta (204 No Content):** Sem body

---

## 📝 Posts

### CRUD Básico de Posts

#### 13. Listar Posts

**Endpoint:** `GET /api/posts/`

**Autenticação:** Não requerida

**Query Parameters:**
- `page` (opcional) - Número da página
- `page_size` (opcional) - Itens por página
- `author` (opcional) - Filtrar por ID do autor
- `has_reply` (opcional) - `true` retorna apenas replies, `false` exclui replies
- `has_media` (opcional) - `true` retorna apenas posts com mídia, `false` exclui posts com mídia
- `is_retweet` (opcional) - `true` retorna apenas retweets, `false` exclui retweets
- `liked_by` (opcional) - Filtrar posts curtidos pelo ID do usuário informado

**Resposta (200 OK):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/posts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "author": {"...": "..."},
      "content": "Meu primeiro post! #python #django",
      "media": [
        {
          "id": 1,
          "type": "image",
          "url": "https://res.cloudinary.com/seu_cloud/image/upload/post_media/img1.jpg",
          "thumbnail": null,
          "order": 0
        }
      ],
      "poll": null,
      "location": null,
      "hashtags": [{"id": 1, "name": "python", "...": "..."}],
      "is_retweet": false,
      "retweet_of": null,
      "in_reply_to": null,
      "scheduled_for": null,
      "is_published": true,
      "stats": {
        "replies": 5,
        "retweets": 10,
        "likes": 25,
        "views": 150
      },
      "is_retweeted": false,
      "is_liked": false,
      "like_id": null,
      "created_at": "2026-02-19T10:00:00Z",
      "updated_at": "2026-02-19T10:00:00Z"
    }
  ]
}
```

---

#### 14. Detalhes de um Post

**Endpoint:** `GET /api/posts/{id}/`

**Autenticação:** Não requerida

**Nota:** Este endpoint **incrementa automaticamente** o contador de views.

**Resposta (200 OK):**
```json
{
  "id": 1,
  "author": {"...": "..."},
  "content": "Post detalhado",
  "media": [],
  "poll": null,
  "location": {"...": "..."},
  "hashtags": [],
  "is_retweet": false,
  "retweet_of": null,
  "in_reply_to": null,
  "scheduled_for": null,
  "is_published": true,
  "stats": {
    "replies": 5,
    "retweets": 10,
    "likes": 25,
    "views": 151
  },
  "is_retweeted": false,
  "is_liked": true,
  "like_id": 42,
  "created_at": "2026-02-19T10:00:00Z",
  "updated_at": "2026-02-19T10:00:00Z"
}
```

**Erros Possíveis:**
- `404 Not Found` - Post não existe

---

#### 15. Criar Post

**Endpoint:** `POST /api/posts/`

**Autenticação:** Requerida

**Content-Type:** `multipart/form-data` (para upload de mídias)

**Body:**
```json
{
  "content": "Meu novo post com #hashtags!",
  "media_files": ["<arquivo1>", "<arquivo2>"],
  "location": {"name": "Torre Eiffel, Paris", "latitude": "48.858844", "longitude": "2.294351"},
  "poll": {"question": "Qual sua linguagem favorita?", "duration_hours": 24, "options": ["Python", "JavaScript", "Go", "Rust"]},
  "scheduled_for": "2026-02-20T15:00:00Z"
}
```

**Validações:**
- `content`: obrigatório, máximo 280 caracteres
- `media_files`: máximo 4 arquivos — Imagens (JPEG, PNG, WEBP): 5MB, GIFs: 15MB, Vídeos (MP4, MOV): 50MB
- `scheduled_for`: deve ser no futuro

**Erros Possíveis:**
- `400 Bad Request` - Validações falharam
- `401 Unauthorized` - Não autenticado

---

#### 16. Atualizar Post

**Endpoint:** `PATCH /api/posts/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Erros Possíveis:**
- `403 Forbidden` - Tentando editar post de outro usuário
- `404 Not Found` - Post não existe

---

#### 17. Deletar Post

**Endpoint:** `DELETE /api/posts/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Resposta (204 No Content):** Sem body

**Nota:** Deleta em cascata: mídias, poll, votos associados

---

#### 18. Feed Personalizado

**Endpoint:** `GET /api/posts/feed/`

**Autenticação:** Requerida

**Descrição:** Retorna posts dos usuários que você segue + seus próprios posts (apenas publicados)

---

### Retweets

#### 19. Retweet Simples

**Endpoint:** `POST /api/posts/{id}/retweet/`

**Autenticação:** Requerida

**Descrição:** Retweeta um post sem comentário. Permite retweet simples mesmo que já exista um quote retweet do mesmo post.

**Erros Possíveis:**
- `400 Bad Request` - Já fez retweet simples deste post
- `401 Unauthorized` - Não autenticado

---

#### 20. Quote Retweet

**Endpoint:** `POST /api/posts/{id}/quote-retweet/`

**Autenticação:** Requerida

**Body:**
```json
{ "content": "Concordo totalmente! 👏" }
```

**Nota:** Múltiplos quote retweets do mesmo post são permitidos.

**Erros Possíveis:**
- `400 Bad Request` - Comentário vazio ou > 280 caracteres
- `401 Unauthorized` - Não autenticado

---

#### 21. Desfazer Retweet

**Endpoint:** `DELETE /api/posts/{id}/unretweet/`

**Autenticação:** Requerida

**Descrição:** Remove apenas o retweet simples. Quote retweets não são afetados.

**Resposta (204 No Content):** Sem body

---

### Replies

#### 22. Criar Reply

**Endpoint:** `POST /api/posts/`

**Body:**
```json
{ "content": "Esta é minha resposta!", "in_reply_to": 5 }
```

---

#### 23. Listar Replies de um Post

**Endpoint:** `GET /api/posts/{id}/replies/`

**Autenticação:** Não requerida

---

#### 24. Thread Completa

**Endpoint:** `GET /api/posts/{id}/thread/`

**Autenticação:** Não requerida

**Descrição:** Retorna o post + todos os posts ancestrais (cadeia de respostas)

---

### Múltiplas Mídias

**Validações:**
- Máximo **4 mídias** por post
- **Imagens** (JPEG, PNG, WEBP): máximo 5MB cada
- **GIFs**: máximo 15MB cada
- **Vídeos** (MP4, MOV): máximo 50MB cada

---

### Posts Agendados

#### 25. Listar Posts Agendados

**Endpoint:** `GET /api/posts/scheduled/`

**Autenticação:** Requerida

**Ordenação:** Por `scheduled_for` ascendente

---

### Trending

#### 26. Posts em Tendência

**Endpoint:** `GET /api/posts/trending/`

**Query Parameters:**
- `limit` (opcional) - padrão: 10, máximo: 50
- `period` (opcional) - `today`, `week`, `month`, `all` (padrão: `all`)

**Ordenação:** Por `views_count` descendente

---

## 🗳️ Polls (Enquetes)

### 27. Detalhes de uma Poll

**Endpoint:** `GET /api/polls/{id}/`

---

### 28. Votar em uma Poll

**Endpoint:** `POST /api/polls/{id}/vote/`

**Body:**
```json
{ "option_id": 1 }
```

**Erros Possíveis:**
- `400 Bad Request` - Já votou nesta poll, poll encerrada, ou option_id inválido
- `401 Unauthorized` - Não autenticado

---

### 29. Desfazer Voto

**Endpoint:** `DELETE /api/polls/{id}/unvote/`

**Resposta (204 No Content):** Sem body

---

### 30. Resultados da Poll

**Endpoint:** `GET /api/polls/{id}/results/`

---

## 📍 Locations (Geolocalização)

### 31. Listar Locations

**Endpoint:** `GET /api/locations/`

---

### 32. Buscar Locations

**Endpoint:** `GET /api/locations/search/?q=paris`

**Limite:** 10 resultados

---

### 33. Locations Próximas

**Endpoint:** `GET /api/locations/nearby/?lat=-23.55&lng=-46.63&radius=10`

---

### 34. Posts de uma Location

**Endpoint:** `GET /api/locations/{id}/posts/`

---

## #️⃣ Hashtags

### 35. Listar Hashtags

**Endpoint:** `GET /api/hashtags/`

---

### 36. Detalhes de uma Hashtag

**Endpoint:** `GET /api/hashtags/{id}/`

---

### 37. Posts de uma Hashtag

**Endpoint:** `GET /api/hashtags/{id}/posts/`

---

### 38. Buscar Hashtags

**Endpoint:** `GET /api/hashtags/search/?q=python`

---

### 39. Hashtags em Tendência

**Endpoint:** `GET /api/hashtags/trending/`

**Query Parameters:**
- `limit` (opcional) - padrão: 10
- `period` (opcional) - `today`, `week`, `month`, `all`

---

## 🔔 Notificações

### 40. Listar Notificações

**Endpoint:** `GET /api/notifications/`

**Tipos:** `like`, `retweet`, `reply`, `follow`, `mention`

**Ordenação:** Não lidas primeiro, depois por `created_at` descendente

---

### 41. Notificações Não Lidas

**Endpoint:** `GET /api/notifications/unread/`

---

### 42. Contador de Não Lidas

**Endpoint:** `GET /api/notifications/unread-count/`

**Resposta (200 OK):**
```json
{ "count": 5 }
```

---

### 43. Marcar Notificação como Lida

**Endpoint:** `POST /api/notifications/{id}/read/`

**Erros Possíveis:**
- `403 Forbidden` - Tentando marcar notificação de outro usuário
- `404 Not Found` - Notificação não existe

---

### 44. Marcar Todas como Lidas

**Endpoint:** `POST /api/notifications/read-all/`

**Resposta (200 OK):**
```json
{ "updated": 10 }
```

---

## 🔍 Busca

### 45. Busca Global

**Endpoint:** `GET /api/search/all/?q=python&limit=5`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "posts": ["..."],
  "users": ["..."],
  "hashtags": ["..."],
  "meta": { "query": "python", "total_results": 3 }
}
```

**Erros Possíveis:**
- `400 Bad Request` - Parâmetro `q` ausente ou < 2 caracteres

---

## ❤️ Curtidas

### 46. Listar Curtidas

**Endpoint:** `GET /api/likes/`

**Query Parameters:**
- `post` (opcional) - Filtrar por ID do post

---

### 47. Curtir um Post

**Endpoint:** `POST /api/likes/`

**Body:**
```json
{ "post": 1 }
```

**Resposta (201 Created):**
```json
{
  "id": 3,
  "user": 1,
  "post": 1,
  "user_username": "user1",
  "created_at": "2026-02-19T16:10:00Z"
}
```

**Nota:** O `id` retornado é o `like_id` necessário para descurtir.

**Erros Possíveis:**
- `400 Bad Request` - Já curtiu este post
- `401 Unauthorized` - Não autenticado

---

### 48. Descurtir um Post

**Endpoint:** `DELETE /api/likes/{like_id}/`

**Autenticação:** Requerida (apenas quem curtiu)

**Resposta (204 No Content):** Sem body

---

## ⚙️ Configurações da Conta

### 49. Atualizar Dados da Conta

**Endpoint:** `PATCH /api/users/{id}/account/`

**Autenticação:** Requerida (apenas o próprio usuário)

**Descrição:** Atualiza dados sensíveis da conta (email, phone, username). Requer confirmação com senha atual.

**Body (todos os campos opcionais, exceto `current_password`):**
```json
{
  "email": "novo@example.com",
  "phone": "11999999999",
  "username": "novousername",
  "current_password": "senha_atual"
}
```

**Validações:**
- `current_password`: obrigatório, deve ser a senha atual correta
- `email`: deve ser único na plataforma
- `phone`: deve ser único na plataforma
- `username`: deve ser único na plataforma

**Resposta (200 OK):**
```json
{
  "id": 1,
  "username": "novousername",
  "email": "novo@example.com",
  "first_name": "User",
  "last_name": "One",
  "bio": "...",
  "profile_image": "...",
  "banner": "...",
  "location": "...",
  "website": "...",
  "birth_date": "1990-05-15",
  "stats": {
    "posts": 150,
    "following": 200,
    "followers": 350
  },
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Senha atual incorreta, email/phone/username já em uso
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Tentando editar conta de outro usuário

---

### 50. Alterar Senha

**Endpoint:** `POST /api/users/{id}/change-password/`

**Autenticação:** Requerida (apenas o próprio usuário)

**Body:**
```json
{
  "current_password": "senha_atual",
  "new_password": "nova_senha",
  "new_password_confirm": "nova_senha"
}
```

**Validações:**
- `current_password`: deve ser a senha atual correta
- `new_password`: mínimo 8 caracteres, deve ser diferente da senha atual
- `new_password_confirm`: deve ser igual a `new_password`

**Resposta (200 OK):**
```json
{
  "detail": "Senha alterada com sucesso."
}
```

**Erros Possíveis:**
- `400 Bad Request` - Senha atual incorreta, senhas não coincidem, nova senha igual à atual, senha muito curta
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Tentando alterar senha de outro usuário

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

```bash
# Registrar
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"pass123","password_confirm":"pass123","birth_date":"1995-06-15"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"testuser","password":"pass123"}'

# Atualizar dados da conta
curl -X PATCH http://localhost:8000/api/users/1/account/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -d '{"email":"novo@example.com","current_password":"pass123"}'

# Alterar senha
curl -X POST http://localhost:8000/api/users/1/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -d '{"current_password":"pass123","new_password":"newpass456","new_password_confirm":"newpass456"}'

# Listar posts de um autor sem replies e sem retweets
curl -X GET "http://localhost:8000/api/posts/?author=1&has_reply=false&is_retweet=false"

# Listar posts curtidos por um usuário
curl -X GET "http://localhost:8000/api/posts/?liked_by=1"
```

---

## 📝 Notas Importantes

### Limites e Validações:

- **Post:** 280 caracteres
- **Bio:** 160 caracteres
- **Senha:** mínimo 8 caracteres
- **Múltiplas Mídias:** Máximo 4 por post
- **Imagens** (JPEG, PNG, WEBP): máximo 5MB
- **GIFs:** máximo 15MB
- **Vídeos:** máximo 50MB
- **profile_image:** máximo 5MB, formatos: JPEG, PNG, WEBP
- **banner:** máximo 5MB, formatos: JPEG, PNG, WEBP
- **Poll:** 2-4 opções, duração 1-168 horas
- **Idade Mínima:** 13 anos

### Armazenamento de Mídia:

- Em **produção**, arquivos são armazenados no **Cloudinary**
- URLs de mídia em produção: `https://res.cloudinary.com/{cloud_name}/...`
- Em **desenvolvimento local**, arquivos são armazenados em `/media/`

### Configurações da Conta — Segurança:

- Alterações de `email`, `phone` e `username` exigem confirmação com `current_password`
- Alteração de senha exige senha atual + nova senha + confirmação
- Nova senha deve ser diferente da senha atual
- Todos os campos de conta são únicos na plataforma

### Retweets — Comportamento:

- Retweet simples e quote retweet são independentes
- `unretweet` remove apenas o retweet simples
- Múltiplos quote retweets do mesmo post são permitidos

### Posts — Campos de Interação:

- `is_liked`: indica se o usuário autenticado curtiu o post
- `like_id`: ID necessário para descurtir via `DELETE /api/likes/{like_id}/`
- `is_retweeted`: indica se o usuário autenticado retweetou o post

### CORS:

- API configurada para aceitar requests de `http://localhost:5173`

### Paginação:

- Padrão: 10 itens por página
- Parâmetros: `page`, `page_size`

### Autenticação:

- Token não expira
- Header: `Authorization: Token <token>`

---

## 🎯 Resumo de Endpoints por Recurso

**Autenticação:** 3 endpoints  
**Usuários:** 6 endpoints  
**Follows:** 3 endpoints  
**Posts:** 13 endpoints  
**Polls:** 4 endpoints  
**Locations:** 4 endpoints  
**Hashtags:** 5 endpoints  
**Notificações:** 5 endpoints  
**Busca:** 1 endpoint  
**Curtidas:** 3 endpoints  
**Configurações da Conta:** 2 endpoints  

**Total:** 49 endpoints ✅

---

**Documentação atualizada em:** 17/03/2026  
**Versão da API:** 4.0  
**Base URL (desenvolvimento):** `http://localhost:8000/api`  
**Base URL (produção):** `https://twitter-clone-api-yu0y.onrender.com/api`  
**Status:** ✅ Produção