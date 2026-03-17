# API Endpoints - Twitter Clone

Documentação completa de todos os endpoints da API REST do Twitter Clone.

**Versão:** 3.0  
**Última atualização:** 16/03/2026  
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

**Resposta (200 OK):**
```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com",
  "first_name": "Novo Nome",
  "last_name": "One",
  "bio": "Nova bio atualizada 🚀",
  "profile_image": "https://res.cloudinary.com/seu_cloud/image/upload/profile_images/user1_new.jpg",
  "banner": "https://res.cloudinary.com/seu_cloud/image/upload/banners/user1_new.jpg",
  "location": "Rio de Janeiro, Brasil",
  "website": "https://novosite.com",
  "birth_date": "1995-10-20",
  "stats": {
    "posts": 150,
    "following": 200,
    "followers": 350
  },
  "created_at": "2026-01-01T10:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Validação falhou (imagem muito grande, formato inválido, idade < 13, etc)
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
    "bio": "Python enthusiast",
    "profile_image": "https://res.cloudinary.com/seu_cloud/image/upload/profile_images/follower1.jpg",
    "banner": null,
    "location": "Brasília, Brasil",
    "website": "",
    "birth_date": null,
    "stats": {
      "posts": 50,
      "following": 100,
      "followers": 80
    },
    "created_at": "2026-01-02T10:00:00Z"
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
    "bio": "Django developer",
    "profile_image": null,
    "banner": null,
    "location": "Porto Alegre, Brasil",
    "website": "https://example.com",
    "birth_date": "1988-03-12",
    "stats": {
      "posts": 200,
      "following": 150,
      "followers": 300
    },
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
      "author": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com",
        "first_name": "User",
        "last_name": "One",
        "bio": "Desenvolvedor Python",
        "profile_image": "https://res.cloudinary.com/seu_cloud/image/upload/profile_images/user1.jpg",
        "banner": null,
        "location": "São Paulo",
        "website": "",
        "birth_date": null,
        "stats": {
          "posts": 150,
          "following": 200,
          "followers": 350
        },
        "created_at": "2026-01-01T10:00:00Z"
      },
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
      "hashtags": [
        {
          "id": 1,
          "name": "python",
          "slug": "python",
          "posts_count": 150,
          "created_at": "2026-01-01T10:00:00Z"
        }
      ],
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
  "author": {
    "id": 1,
    "username": "user1",
    "...": "..."
  },
  "content": "Post detalhado",
  "media": [],
  "poll": null,
  "location": {
    "id": 1,
    "name": "São Paulo, Brasil",
    "latitude": "-23.550520",
    "longitude": "-46.633308",
    "has_coordinates": true,
    "created_at": "2026-02-19T10:00:00Z"
  },
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
  "location": {
    "name": "Torre Eiffel, Paris",
    "latitude": "48.858844",
    "longitude": "2.294351"
  },
  "poll": {
    "question": "Qual sua linguagem favorita?",
    "duration_hours": 24,
    "options": ["Python", "JavaScript", "Go", "Rust"]
  },
  "scheduled_for": "2026-02-20T15:00:00Z"
}
```

**Todos os campos são opcionais exceto `content`**

**Validações:**
- `content`: obrigatório, máximo 280 caracteres
- `media_files`: máximo 4 arquivos
  - Imagens (JPEG, PNG, WEBP): máximo 5MB cada
  - GIFs: máximo 15MB cada
  - Vídeos (MP4, MOV): máximo 50MB cada
- `poll`:
  - mínimo 2 opções, máximo 4
  - `duration_hours`: mínimo 1h, máximo 168h (7 dias)
  - opções sem duplicatas
- `location`:
  - `latitude`: -90 a 90
  - `longitude`: -180 a 180
  - ambas devem ser fornecidas juntas
- `scheduled_for`: deve ser no futuro

**Resposta (201 Created):**
```json
{
  "id": 2,
  "author": {"...": "..."},
  "content": "Meu novo post com #hashtags!",
  "media": [
    {
      "id": 1,
      "type": "image",
      "url": "https://res.cloudinary.com/seu_cloud/image/upload/post_media/img1.jpg",
      "thumbnail": null,
      "order": 0
    }
  ],
  "poll": {"...": "..."},
  "location": {"...": "..."},
  "hashtags": [
    {
      "id": 3,
      "name": "hashtags",
      "slug": "hashtags",
      "posts_count": 1,
      "created_at": "2026-02-19T11:00:00Z"
    }
  ],
  "is_retweet": false,
  "retweet_of": null,
  "in_reply_to": null,
  "scheduled_for": "2026-02-20T15:00:00Z",
  "is_published": false,
  "stats": {
    "replies": 0,
    "retweets": 0,
    "likes": 0,
    "views": 0
  },
  "is_retweeted": false,
  "is_liked": false,
  "like_id": null,
  "created_at": "2026-02-19T11:00:00Z",
  "updated_at": "2026-02-19T11:00:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Validações falharam
- `401 Unauthorized` - Não autenticado

---

#### 16. Atualizar Post

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
  "author": {"...": "..."},
  "content": "Conteúdo atualizado",
  "media": [],
  "poll": null,
  "location": null,
  "hashtags": [],
  "is_retweet": false,
  "retweet_of": null,
  "in_reply_to": null,
  "scheduled_for": null,
  "is_published": true,
  "stats": {
    "replies": 0,
    "retweets": 0,
    "likes": 0,
    "views": 5
  },
  "is_retweeted": false,
  "is_liked": false,
  "like_id": null,
  "created_at": "2026-02-19T11:00:00Z",
  "updated_at": "2026-02-19T11:30:00Z"
}
```

**Erros Possíveis:**
- `403 Forbidden` - Tentando editar post de outro usuário
- `404 Not Found` - Post não existe

---

#### 17. Deletar Post

**Endpoint:** `DELETE /api/posts/{id}/`

**Autenticação:** Requerida (apenas o autor)

**Resposta (204 No Content):**
Sem body

**Nota:** Deleta em cascata: mídias, poll, votos associados

**Erros Possíveis:**
- `403 Forbidden` - Tentando deletar post de outro usuário
- `404 Not Found` - Post não existe

---

#### 18. Feed Personalizado

**Endpoint:** `GET /api/posts/feed/`

**Autenticação:** Requerida

**Descrição:** Retorna posts dos usuários que você segue + seus próprios posts (apenas publicados)

**Resposta (200 OK):**
```json
[
  {
    "id": 5,
    "author": {
      "id": 2,
      "username": "following1",
      "...": "..."
    },
    "content": "Post de alguém que eu sigo",
    "media": [],
    "poll": null,
    "location": null,
    "hashtags": [],
    "is_retweet": false,
    "retweet_of": null,
    "in_reply_to": null,
    "scheduled_for": null,
    "is_published": true,
    "stats": {
      "replies": 5,
      "retweets": 3,
      "likes": 15,
      "views": 100
    },
    "is_retweeted": false,
    "is_liked": false,
    "like_id": null,
    "created_at": "2026-02-19T12:00:00Z",
    "updated_at": "2026-02-19T12:00:00Z"
  }
]
```

---

### Retweets

#### 19. Retweet Simples

**Endpoint:** `POST /api/posts/{id}/retweet/`

**Autenticação:** Requerida

**Body:** Vazio

**Descrição:** Retweeta um post sem comentário. Permite retweet simples mesmo que já exista um quote retweet do mesmo post.

**Resposta (201 Created):**
```json
{
  "id": 10,
  "author": {
    "id": 1,
    "username": "user1",
    "...": "..."
  },
  "content": "",
  "media": [],
  "poll": null,
  "location": null,
  "hashtags": [],
  "is_retweet": true,
  "retweet_of": 5,
  "in_reply_to": null,
  "scheduled_for": null,
  "is_published": true,
  "stats": {
    "replies": 0,
    "retweets": 0,
    "likes": 0,
    "views": 0
  },
  "is_retweeted": false,
  "is_liked": false,
  "like_id": null,
  "created_at": "2026-02-19T13:00:00Z",
  "updated_at": "2026-02-19T13:00:00Z"
}
```

**Nota:** Incrementa `retweets_count` do post original automaticamente.

**Erros Possíveis:**
- `400 Bad Request` - Já fez retweet simples deste post
- `401 Unauthorized` - Não autenticado

---

#### 20. Quote Retweet (Retweet com Comentário)

**Endpoint:** `POST /api/posts/{id}/quote-retweet/`

**Autenticação:** Requerida

**Body:**
```json
{
  "content": "Concordo totalmente! 👏"
}
```

**Validações:**
- `content`: obrigatório, máximo 280 caracteres

**Nota:** Múltiplos quote retweets do mesmo post são permitidos.

**Resposta (201 Created):**
```json
{
  "id": 11,
  "author": {
    "id": 1,
    "username": "user1",
    "...": "..."
  },
  "content": "Concordo totalmente! 👏",
  "media": [],
  "poll": null,
  "location": null,
  "hashtags": [],
  "is_retweet": true,
  "retweet_of": 5,
  "in_reply_to": null,
  "scheduled_for": null,
  "is_published": true,
  "stats": {
    "replies": 0,
    "retweets": 0,
    "likes": 0,
    "views": 0
  },
  "is_retweeted": false,
  "is_liked": false,
  "like_id": null,
  "created_at": "2026-02-19T13:05:00Z",
  "updated_at": "2026-02-19T13:05:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Comentário vazio ou > 280 caracteres
- `401 Unauthorized` - Não autenticado

---

#### 21. Desfazer Retweet

**Endpoint:** `DELETE /api/posts/{id}/unretweet/`

**Autenticação:** Requerida

**Descrição:** Remove apenas o retweet simples do post. Quote retweets não são afetados.

**Resposta (204 No Content):**
Sem body

**Nota:** Decrementa `retweets_count` do post original automaticamente.

**Erros Possíveis:**
- `400 Bad Request` - Você não fez retweet simples deste post
- `401 Unauthorized` - Não autenticado

---

### Replies

#### 22. Criar Reply (Resposta)

**Endpoint:** `POST /api/posts/`

**Autenticação:** Requerida

**Body:**
```json
{
  "content": "Esta é minha resposta!",
  "in_reply_to": 5
}
```

**Resposta (201 Created):**
```json
{
  "id": 12,
  "author": {"...": "..."},
  "content": "Esta é minha resposta!",
  "media": [],
  "poll": null,
  "location": null,
  "hashtags": [],
  "is_retweet": false,
  "retweet_of": null,
  "in_reply_to": 5,
  "scheduled_for": null,
  "is_published": true,
  "stats": {
    "replies": 0,
    "retweets": 0,
    "likes": 0,
    "views": 0
  },
  "is_retweeted": false,
  "is_liked": false,
  "like_id": null,
  "created_at": "2026-02-19T13:10:00Z",
  "updated_at": "2026-02-19T13:10:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Post a responder não existe

---

#### 23. Listar Replies de um Post

**Endpoint:** `GET /api/posts/{id}/replies/`

**Autenticação:** Não requerida

**Descrição:** Retorna todas as respostas diretas de um post

**Resposta (200 OK):**
```json
[
  {
    "id": 12,
    "author": {"...": "..."},
    "content": "Primeira resposta",
    "in_reply_to": 5,
    "...": "..."
  },
  {
    "id": 13,
    "author": {"...": "..."},
    "content": "Segunda resposta",
    "in_reply_to": 5,
    "...": "..."
  }
]
```

---

#### 24. Thread Completa

**Endpoint:** `GET /api/posts/{id}/thread/`

**Autenticação:** Não requerida

**Descrição:** Retorna o post + todos os posts ancestrais (cadeia de respostas)

**Exemplo:** Se o post C respondeu B, e B respondeu A, retorna [A, B, C]

**Resposta (200 OK):**
```json
[
  {
    "id": 5,
    "content": "Post original (A)",
    "in_reply_to": null,
    "...": "..."
  },
  {
    "id": 10,
    "content": "Resposta ao A (B)",
    "in_reply_to": 5,
    "...": "..."
  },
  {
    "id": 12,
    "content": "Resposta ao B (C)",
    "in_reply_to": 10,
    "...": "..."
  }
]
```

---

### Múltiplas Mídias

**Nota:** Upload de mídias é feito através do endpoint de criar post (endpoint 15). Arquivos são armazenados no Cloudinary em produção.

**Validações:**
- Máximo **4 mídias** por post
- **Imagens** (JPEG, PNG, WEBP): máximo 5MB cada
- **GIFs**: máximo 15MB cada
- **Vídeos** (MP4, MOV): máximo 50MB cada
- Ordem preservada automaticamente

**Exemplo de Upload (multipart/form-data):**
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token SEU_TOKEN" \
  -F "content=Post com múltiplas imagens!" \
  -F "media_files=@image1.jpg" \
  -F "media_files=@animated.gif" \
  -F "media_files=@video.mp4"
```

---

### Posts Agendados

#### 25. Listar Posts Agendados

**Endpoint:** `GET /api/posts/scheduled/`

**Autenticação:** Requerida

**Descrição:** Lista apenas os posts agendados (futuro) do usuário autenticado

**Resposta (200 OK):**
```json
[
  {
    "id": 20,
    "content": "Post agendado para amanhã",
    "author": {"...": "..."},
    "scheduled_for": "2026-02-20T10:00:00Z",
    "is_published": false
  }
]
```

**Ordenação:** Por `scheduled_for` ascendente (mais próximo primeiro)

---

### Trending (Posts Mais Vistos)

#### 26. Posts em Tendência

**Endpoint:** `GET /api/posts/trending/`

**Autenticação:** Não requerida

**Query Parameters:**
- `limit` (opcional) - Número de posts (padrão: 10, máximo: 50)
- `period` (opcional) - Período: `today`, `week`, `month`, `all` (padrão: `all`)

**Resposta (200 OK):**
```json
[
  {
    "id": 30,
    "content": "Post viral!",
    "stats": {
      "replies": 500,
      "retweets": 1000,
      "likes": 5000,
      "views": 50000
    },
    "...": "..."
  }
]
```

**Ordenação:** Por `views_count` descendente

---

## 🗳️ Polls (Enquetes)

**Nota:** Polls são criadas através do endpoint de criar post (endpoint 15)

### 27. Detalhes de uma Poll

**Endpoint:** `GET /api/polls/{id}/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "id": 1,
  "post": 5,
  "question": "Qual sua linguagem favorita?",
  "duration_hours": 24,
  "ends_at": "2026-02-20T10:00:00Z",
  "is_ended": false,
  "total_votes": 150,
  "options": [
    {
      "id": 1,
      "text": "Python",
      "votes": 80,
      "percentage": 53.33,
      "order": 0
    },
    {
      "id": 2,
      "text": "JavaScript",
      "votes": 50,
      "percentage": 33.33,
      "order": 1
    }
  ],
  "user_voted_option_id": null
}
```

---

### 28. Votar em uma Poll

**Endpoint:** `POST /api/polls/{id}/vote/`

**Autenticação:** Requerida

**Body:**
```json
{
  "option_id": 1
}
```

**Resposta (200 OK):**
```json
{
  "id": 1,
  "total_votes": 151,
  "options": [
    {
      "id": 1,
      "text": "Python",
      "votes": 81,
      "percentage": 53.64,
      "order": 0
    }
  ],
  "user_voted_option_id": 1
}
```

**Erros Possíveis:**
- `400 Bad Request` - Já votou nesta poll, poll encerrada, ou option_id inválido
- `401 Unauthorized` - Não autenticado

---

### 29. Desfazer Voto

**Endpoint:** `DELETE /api/polls/{id}/unvote/`

**Autenticação:** Requerida

**Resposta (204 No Content):**
Sem body

**Erros Possíveis:**
- `400 Bad Request` - Não votou nesta poll, ou poll encerrada
- `401 Unauthorized` - Não autenticado

---

### 30. Resultados da Poll

**Endpoint:** `GET /api/polls/{id}/results/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "question": "Qual sua linguagem favorita?",
  "ends_at": "2026-02-20T10:00:00Z",
  "is_ended": false,
  "total_votes": 151,
  "options": [
    {
      "text": "Python",
      "votes": 81,
      "percentage": 53.64
    }
  ]
}
```

---

## 📍 Locations (Geolocalização)

**Nota:** Locations são criadas através do endpoint de criar post (endpoint 15)

### 31. Listar Locations

**Endpoint:** `GET /api/locations/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Torre Eiffel, Paris",
      "latitude": "48.858844",
      "longitude": "2.294351",
      "has_coordinates": true,
      "created_at": "2026-02-19T10:00:00Z"
    }
  ]
}
```

---

### 32. Buscar Locations

**Endpoint:** `GET /api/locations/search/`

**Autenticação:** Não requerida

**Query Parameters:**
- `q` (obrigatório) - Termo de busca

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Paris, França",
    "latitude": "48.8566",
    "longitude": "2.3522",
    "has_coordinates": true,
    "created_at": "2026-02-19T10:00:00Z"
  }
]
```

**Limite:** 10 resultados

**Erros Possíveis:**
- `400 Bad Request` - Parâmetro `q` não fornecido

---

### 33. Locations Próximas

**Endpoint:** `GET /api/locations/nearby/`

**Autenticação:** Não requerida

**Query Parameters:**
- `lat` (opcional) - Latitude (padrão: 0)
- `lng` (opcional) - Longitude (padrão: 0)
- `radius` (opcional) - Raio em km (padrão: 10)

**Resposta (200 OK):**
```json
[
  {
    "id": 10,
    "name": "Museu do Louvre",
    "latitude": "48.860611",
    "longitude": "2.337644",
    "has_coordinates": true,
    "created_at": "2026-02-19T12:00:00Z"
  }
]
```

**Erros Possíveis:**
- `400 Bad Request` - Coordenadas inválidas

---

### 34. Posts de uma Location

**Endpoint:** `GET /api/locations/{id}/posts/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
[
  {
    "id": 5,
    "content": "Visitando a Torre Eiffel!",
    "location": {
      "id": 1,
      "name": "Torre Eiffel, Paris"
    },
    "...": "..."
  }
]
```

---

## #️⃣ Hashtags

### 35. Listar Hashtags

**Endpoint:** `GET /api/hashtags/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "python",
      "slug": "python",
      "posts_count": 1500,
      "created_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

---

### 36. Detalhes de uma Hashtag

**Endpoint:** `GET /api/hashtags/{id}/`

**Autenticação:** Não requerida

**Resposta (200 OK):**
```json
{
  "id": 1,
  "name": "python",
  "slug": "python",
  "posts_count": 1500,
  "created_at": "2026-01-01T10:00:00Z"
}
```

---

### 37. Posts de uma Hashtag

**Endpoint:** `GET /api/hashtags/{id}/posts/`

**Autenticação:** Não requerida

**Query Parameters:**
- `limit` (opcional) - Número de posts (padrão: 20)

**Resposta (200 OK):**
```json
[
  {
    "id": 10,
    "content": "Post sobre #python",
    "hashtags": [
      {
        "id": 1,
        "name": "python"
      }
    ],
    "...": "..."
  }
]
```

---

### 38. Buscar Hashtags

**Endpoint:** `GET /api/hashtags/search/`

**Autenticação:** Não requerida

**Query Parameters:**
- `q` (obrigatório) - Termo de busca

**Resposta (200 OK):**
```json
[
  {
    "id": 1,
    "name": "python",
    "slug": "python",
    "posts_count": 1500,
    "created_at": "2026-01-01T10:00:00Z"
  }
]
```

**Erros Possíveis:**
- `400 Bad Request` - Parâmetro `q` não fornecido

---

### 39. Hashtags em Tendência

**Endpoint:** `GET /api/hashtags/trending/`

**Autenticação:** Não requerida

**Query Parameters:**
- `limit` (opcional) - Número de hashtags (padrão: 10)
- `period` (opcional) - Período: `today`, `week`, `month`, `all` (padrão: `all`)

**Resposta (200 OK):**
```json
{
  "meta": {
    "period": "week",
    "limit": 10,
    "total": 10,
    "generated_at": "2026-02-19T14:00:00Z"
  },
  "results": [
    {
      "id": 1,
      "name": "python",
      "slug": "python",
      "posts_count": 1500,
      "recent_posts_count": 150,
      "created_at": "2026-01-01T10:00:00Z"
    }
  ]
}
```

---

## 🔔 Notificações

### 40. Listar Notificações

**Endpoint:** `GET /api/notifications/`

**Autenticação:** Requerida

**Resposta (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "actor": {
        "id": 2,
        "username": "bob",
        "...": "..."
      },
      "notification_type": "like",
      "notification_type_display": "Curtida",
      "post": 5,
      "post_preview": {
        "id": 5,
        "content": "Meu post que foi curtido",
        "author": {
          "id": 1,
          "username": "alice"
        }
      },
      "is_read": false,
      "created_at": "2026-02-19T14:30:00Z"
    }
  ]
}
```

**Tipos de notificação:** `like`, `retweet`, `reply`, `follow`, `mention`

**Ordenação:** Não lidas primeiro, depois por `created_at` descendente

---

### 41. Notificações Não Lidas

**Endpoint:** `GET /api/notifications/unread/`

**Autenticação:** Requerida

**Resposta (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": ["..."]
}
```

---

### 42. Contador de Não Lidas

**Endpoint:** `GET /api/notifications/unread-count/`

**Autenticação:** Requerida

**Resposta (200 OK):**
```json
{
  "count": 5
}
```

---

### 43. Marcar Notificação como Lida

**Endpoint:** `POST /api/notifications/{id}/read/`

**Autenticação:** Requerida

**Body:** Vazio

**Resposta (200 OK):**
```json
{
  "id": 1,
  "is_read": true,
  "...": "..."
}
```

**Erros Possíveis:**
- `403 Forbidden` - Tentando marcar notificação de outro usuário
- `404 Not Found` - Notificação não existe

---

### 44. Marcar Todas como Lidas

**Endpoint:** `POST /api/notifications/read-all/`

**Autenticação:** Requerida

**Body:** Vazio

**Resposta (200 OK):**
```json
{
  "updated": 10
}
```

---

## 🔍 Busca

### 45. Busca Global

**Endpoint:** `GET /api/search/all/`

**Autenticação:** Não requerida

**Query Parameters:**
- `q` (obrigatório) - Termo de busca (mínimo 2 caracteres)
- `limit` (opcional) - Resultados por tipo (padrão: 5, máximo: 20)

**Resposta (200 OK):**
```json
{
  "posts": ["..."],
  "users": ["..."],
  "hashtags": ["..."],
  "meta": {
    "query": "python",
    "total_results": 3
  }
}
```

**Erros Possíveis:**
- `400 Bad Request` - Parâmetro `q` ausente ou < 2 caracteres

---

## ❤️ Curtidas

### 46. Listar Curtidas

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
      "created_at": "2026-02-19T16:00:00Z"
    }
  ]
}
```

---

### 47. Curtir um Post

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
  "created_at": "2026-02-19T16:10:00Z"
}
```

**Erros Possíveis:**
- `400 Bad Request` - Já curtiu este post
- `401 Unauthorized` - Não autenticado

---

### 48. Descurtir um Post

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
  -d '{"username":"testuser","email":"test@test.com","password":"pass123","password_confirm":"pass123","birth_date":"1995-06-15"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"identifier":"testuser","password":"pass123"}'

# Criar Post com Hashtags
curl -X POST http://localhost:8000/api/posts/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -d '{"content":"Meu primeiro post com #python e #django!"}'

# Upload de Imagens e GIF
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Token SEU_TOKEN_AQUI" \
  -F "content=Post com imagens!" \
  -F "media_files=@image1.jpg" \
  -F "media_files=@animated.gif"

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
- URLs de mídia em produção seguem o padrão: `https://res.cloudinary.com/{cloud_name}/...`
- Em **desenvolvimento local**, arquivos são armazenados em `/media/`

### Funcionalidades Automáticas:

- **Hashtags:** Extraídas automaticamente do conteúdo
- **Views:** Incrementadas ao visualizar post
- **Notificações:** Criadas automaticamente para likes, retweets, replies, follows, mentions
- **Stats:** Calculados dinamicamente (posts_count, followers_count, etc)
- **Retweets/Unretweets:** Contadores atualizados automaticamente

### Retweets — Comportamento:

- Retweet simples e quote retweet são independentes — é possível ter ambos no mesmo post
- `unretweet` remove apenas o retweet simples, nunca afeta quote retweets
- Múltiplos quote retweets do mesmo post são permitidos
- `is_retweeted: true` indica que o usuário autenticado fez algum tipo de retweet (simples ou quote)

### Posts — Campos de Interação:

- `is_liked`: indica se o usuário autenticado curtiu o post
- `like_id`: ID da curtida do usuário autenticado (necessário para descurtir via `DELETE /api/likes/{like_id}/`)
- `is_retweeted`: indica se o usuário autenticado retweetou o post (simples ou quote)
- Campos retornam `false`/`null` para usuários não autenticados

### CORS:

- API configurada para aceitar requests de `http://localhost:5173`

### Paginação:

- Padrão: 10 itens por página
- Parâmetros: `page`, `page_size`

### Autenticação:

- Token não expira (implementação simples)
- Token enviado no header: `Authorization: Token <token>`

---

## 🎯 Resumo de Endpoints por Recurso

**Autenticação:** 3 endpoints  
**Usuários:** 6 endpoints  
**Follows:** 3 endpoints  
**Posts:** 13 endpoints (CRUD + Retweets + Replies + Feed + Trending + Scheduled)  
**Polls:** 4 endpoints  
**Locations:** 4 endpoints  
**Hashtags:** 5 endpoints  
**Notificações:** 5 endpoints  
**Busca:** 1 endpoint  
**Curtidas:** 3 endpoints  

**Total:** 47 endpoints ✅

---

**Documentação atualizada em:** 16/03/2026  
**Versão da API:** 3.0  
**Base URL (desenvolvimento):** `http://localhost:8000/api`  
**Base URL (produção):** `https://twitter-clone-api-yu0y.onrender.com/api`  
**Status:** ✅ Produção