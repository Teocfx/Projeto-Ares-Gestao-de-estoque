# 🚀 API REST - ARES Sistema de Gestão de Estoque

## 📋 Visão Geral

API REST completa do Sistema ARES utilizando Django REST Framework com autenticação JWT, documentação Swagger/OpenAPI, rate limiting e versionamento.

**Base URL:** `http://localhost:8000/api/v1/`  
**Documentação:** `http://localhost:8000/api/v1/docs/` (Swagger UI)  
**ReDoc:** `http://localhost:8000/api/v1/redoc/`

---

## 🔐 Autenticação

### Obter Token JWT

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "admin",
  "password": "senha123"
}
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Renovar Token

```bash
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token nas Requisições

```bash
GET /api/v1/products/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📦 Produtos

### Categorias

- **GET** `/api/v1/categories/` - Listar categorias
- **POST** `/api/v1/categories/` - Criar categoria (admin)
- **GET** `/api/v1/categories/{id}/` - Detalhes
- **GET** `/api/v1/categories/{id}/products/` - Produtos da categoria

### Unidades de Medida

- **GET** `/api/v1/units/` - Listar unidades
- **POST** `/api/v1/units/` - Criar unidade (admin)
- **GET** `/api/v1/units/{id}/` - Detalhes

### Produtos

- **GET** `/api/v1/products/` - Listar produtos
- **POST** `/api/v1/products/` - Criar produto
- **GET** `/api/v1/products/{id}/` - Detalhes
- **PUT** `/api/v1/products/{id}/` - Atualizar
- **DELETE** `/api/v1/products/{id}/` - Remover (soft delete)

**Actions Especiais:**
- **GET** `/api/v1/products/low_stock/` - Produtos com estoque baixo
- **GET** `/api/v1/products/expired/` - Produtos vencidos
- **GET** `/api/v1/products/stats/` - Estatísticas gerais
- **GET** `/api/v1/products/{id}/movements/` - Movimentações do produto

**Exemplo - Criar Produto:**
```json
{
  "sku": "PROD-001",
  "name": "Notebook Dell",
  "description": "Notebook i7 16GB RAM",
  "category_id": 1,
  "unit_id": 1,
  "current_stock": 10,
  "min_stock": 5,
  "unit_price": 3500.00
}
```

**Filtros Disponíveis:**
- `?name=notebook` - Busca por nome
- `?sku=PROD` - Busca por SKU
- `?category=1` - Filtrar por categoria
- `?low_stock=true` - Apenas estoque baixo
- `?ordering=-created_at` - Ordenar

---

## 📊 Movimentações

- **GET** `/api/v1/movements/` - Listar movimentações
- **POST** `/api/v1/movements/` - Criar movimentação
- **GET** `/api/v1/movements/{id}/` - Detalhes

**Actions Especiais:**
- **POST** `/api/v1/movements/bulk_create/` - Criar múltiplas (lote)
- **GET** `/api/v1/movements/stats/` - Estatísticas
- **GET** `/api/v1/movements/by_product/?product_id=1` - Por produto
- **GET** `/api/v1/movements/by_type/?type=ENTRADA` - Por tipo

**Exemplo - Criar Movimentação (Entrada):**
```json
{
  "product_id": 1,
  "type": "ENTRADA",
  "quantity": 50,
  "document": "NF-001234",
  "notes": "Compra de fornecedor XYZ"
}
```

**Exemplo - Criar em Lote:**
```json
{
  "movements": [
    {
      "product_id": 1,
      "type": "ENTRADA",
      "quantity": 10,
      "document": "NF-001"
    },
    {
      "product_id": 2,
      "type": "SAIDA",
      "quantity": 5,
      "notes": "Venda"
    }
  ]
}
```

**Tipos de Movimentação:**
- `ENTRADA` - Entrada de estoque
- `SAIDA` - Saída de estoque
- `AJUSTE` - Ajuste manual

---

## 👥 Usuários e Perfis

### Usuários

- **GET** `/api/v1/users/` - Listar usuários (admin)
- **GET** `/api/v1/users/{id}/` - Detalhes
- **GET** `/api/v1/users/me/` - Dados do usuário autenticado

### Perfis

- **GET** `/api/v1/perfis/` - Listar perfis (admin)
- **GET** `/api/v1/perfis/{id}/` - Detalhes
- **GET** `/api/v1/perfis/stats/` - Estatísticas

**Tipos de Perfil:**
- `REPR_LEGAL` - Representante Legal (acesso total)
- `REPR_DELEGADO` - Representante Delegado (administrativo)
- `OPERADOR` - Operador (operacional)

---

## 📝 Logs de Auditoria

- **GET** `/api/v1/audit-logs/` - Listar logs (admin)
- **GET** `/api/v1/audit-logs/{id}/` - Detalhes
- **GET** `/api/v1/audit-logs/stats/` - Estatísticas
- **GET** `/api/v1/audit-logs/by_user/?user_id=1` - Por usuário
- **GET** `/api/v1/audit-logs/by_model/?model=product` - Por modelo

**Filtros:**
- `?action=CREATE` - Por ação (CREATE, UPDATE, DELETE)
- `?date_from=2025-01-01` - Data inicial
- `?date_to=2025-12-31` - Data final

---

## 🔍 Filtros, Busca e Ordenação

Todos os endpoints suportam:

### Filtros
```bash
GET /api/v1/products/?category=1&unit=2
```

### Busca
```bash
GET /api/v1/products/?search=notebook
```

### Ordenação
```bash
GET /api/v1/products/?ordering=-created_at
GET /api/v1/products/?ordering=name
```

### Paginação
```bash
GET /api/v1/products/?page=2
```

**Resposta Paginada:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/products/?page=3",
  "previous": "http://localhost:8000/api/v1/products/?page=1",
  "results": [...]
}
```

---

## ⚡ Rate Limiting

- **Anônimo:** 100 requisições/hora
- **Autenticado:** 1000 requisições/hora

**Headers de Resposta:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1635724800
```

---

## 🛡️ Permissões

### Níveis de Acesso

| Recurso | Leitura | Criar | Editar | Deletar |
|---------|---------|-------|--------|---------|
| **Categorias** | Todos | Admin | Admin | Admin |
| **Unidades** | Todos | Admin | Admin | Admin |
| **Produtos** | Todos | Staff | Staff | Staff |
| **Movimentações** | Todos | Staff | ❌ | ❌ |
| **Usuários** | Self/Admin | ❌ | ❌ | ❌ |
| **Audit Logs** | Admin | ❌ | ❌ | ❌ |

**Nota:** Movimentações não podem ser editadas/deletadas (auditoria).

---

## 📊 Estatísticas

### Produtos
```bash
GET /api/v1/products/stats/
```

**Resposta:**
```json
{
  "total_products": 150,
  "total_categories": 12,
  "total_stock_value": 125000.50,
  "low_stock_count": 8,
  "expired_count": 2,
  "top_categories": [
    {"category__name": "Eletrônicos", "count": 45}
  ]
}
```

### Movimentações
```bash
GET /api/v1/movements/stats/?date_from=2025-01-01&date_to=2025-12-31
```

**Resposta:**
```json
{
  "total_movements": 500,
  "total_entries": 300,
  "total_exits": 180,
  "total_adjustments": 20,
  "quantity_entered": 5000.00,
  "quantity_exited": 3200.00,
  "most_moved_products": [...]
}
```

---

## 🚨 Tratamento de Erros

### Códigos HTTP

- `200` OK
- `201` Created
- `400` Bad Request (validação)
- `401` Unauthorized (sem autenticação)
- `403` Forbidden (sem permissão)
- `404` Not Found
- `429` Too Many Requests (rate limit)
- `500` Internal Server Error

### Formato de Erro

```json
{
  "detail": "Descrição do erro",
  "field_name": ["Erro específico do campo"]
}
```

**Exemplo:**
```json
{
  "sku": ["SKU 'PROD-001' já existe."],
  "quantity": ["Estoque insuficiente. Disponível: 5 UN"]
}
```

---

## 🔧 Exemplos de Uso

### Python (requests)

```python
import requests

# Obter token
response = requests.post(
    'http://localhost:8000/api/v1/auth/token/',
    json={'username': 'admin', 'password': 'senha123'}
)
token = response.json()['access']

# Listar produtos
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(
    'http://localhost:8000/api/v1/products/',
    headers=headers
)
products = response.json()['results']
```

### JavaScript (fetch)

```javascript
// Obter token
const authResponse = await fetch('http://localhost:8000/api/v1/auth/token/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'admin', password: 'senha123'})
});
const {access} = await authResponse.json();

// Criar produto
const productResponse = await fetch('http://localhost:8000/api/v1/products/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access}`
  },
  body: JSON.stringify({
    sku: 'PROD-002',
    name: 'Mouse Logitech',
    category_id: 1,
    unit_id: 1,
    current_stock: 20,
    min_stock: 10,
    unit_price: 89.90
  })
});
```

### cURL

```bash
# Obter token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"senha123"}'

# Criar movimentação
curl -X POST http://localhost:8000/api/v1/movements/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  -d '{
    "product_id": 1,
    "type": "ENTRADA",
    "quantity": 100,
    "document": "NF-5678"
  }'
```

---

## 🔗 Links Úteis

- **Swagger UI:** http://localhost:8000/api/v1/docs/
- **ReDoc:** http://localhost:8000/api/v1/redoc/
- **JSON Schema:** http://localhost:8000/api/v1/swagger.json

---

## 📝 Notas Importantes

1. **JWT Expiration:**
   - Access Token: 2 horas
   - Refresh Token: 7 dias

2. **Paginação:**
   - Padrão: 20 items por página
   - Máximo: 100 items por página

3. **Soft Delete:**
   - Produtos e categorias usam soft delete (`is_active=False`)
   - Movimentações são imutáveis (auditoria)

4. **CORS:**
   - Configurado para localhost:3000 e localhost:8000
   - Ajustar em produção

5. **Versionamento:**
   - Versão atual: v1
   - URL: `/api/v1/`
   - Versão futura: `/api/v2/`

---

**Data:** 25 de novembro de 2025  
**Versão API:** 1.0.0  
**Status:** Produção Ready ✅
