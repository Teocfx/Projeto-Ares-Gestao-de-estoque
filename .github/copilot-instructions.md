# Guia: App Web de Gestão de Estoque

> Guia para um **aplicativo de gestão de estoque** usando Django, SCSS, JS.

---

## 1 — Visão geral do projeto

Aplicação web para gerenciamento de produtos, fornecedores, estoques e movimentações. Priorizamos UX responsivo (desktop/tablet/mobile), desempenho e simplicidade no desenvolvimento.

* **Backend**: Django 5.2.x (Python 3.12+)
* **Frontend**: JavaScript/Webpack na pasta `frontend/`
* **Banco de Dados**: PostgreSQL em produção; SQLite para desenvolvimento/testes
* **Ambiente local**: Python 3.12+ e Node.js v22.13.1+
* **Gerenciamento de Versões**: asdf (recomendado), NVM, virtualenv, conda, pyenv

> **⚠️ IMPORTANTE - Configuração Local de Ambiente:**
>
> Antes de executar qualquer comando Python ou npm, **SEMPRE pergunte ao usuário**:
> 1. "Qual comando você usa para ativar o ambiente virtual Python?"
>    - Exemplos: `asdf install`, `source venv/bin/activate`, `conda activate <nome>`
> 2. "Qual comando você usa para ativar a versão do Node.js (se aplicável)?"
>    - Exemplos: `asdf install`, `nvm use`, ou nenhum se usar versão global
>
> Após obter as respostas, crie/atualize o arquivo `.github/copilot-local.md` com os comandos específicos.

---

## 2 — Funcionalidades do Sistema

### 2.1 Autenticação
- Login com e-mail/usuário e senha
- Recuperação de senha via e-mail
- Gerenciamento de permissões (Admin, Gestor, Operador)
- Logout

### 2.2 Dashboard
- Valor total do estoque
- Itens cadastrados
- Produtos mais vendidos
- Últimas movimentações
- Alertas (estoque crítico, validade próxima/vencida)

### 2.3 Produtos
- CRUD completo (Criar, Listar, Editar, Excluir)
- Campos: Nome, Código/SKU, Categoria, Quantidade, Estoque Mínimo, Validade
- Busca e filtros por categoria
- Alertas automáticos (crítico/baixo/OK)

### 2.4 Movimentações
- Registrar entradas (compras, devoluções)
- Registrar saídas (vendas, baixas)
- Histórico filtrável por período e tipo
- Documentos fiscais (NF, CF-e)
- Auditoria (usuário, data/hora)

### 2.5 Relatórios
- Relatórios de estoque
- Relatórios de movimentações
- Relatórios de vencimentos
- Filtro por período
- Exportação para PDF

### 2.6 Configurações
- Configurações gerais (modo offline, notificações)
- Dados fiscais (NCM, CFOP, CST/CSOSN)
- Gerenciamento de usuários e permissões
- Perfil do usuário

---

## 3 — Estrutura de pastas

```
project/
├── backend/
│   ├── core/              # Funcionalidades compartilhadas
│   ├── autenticacao/      # Login, logout, recuperação senha
│   ├── produtos/          # CRUD de produtos
│   ├── movimentacoes/     # Entradas e saídas
│   ├── relatorios/        # Geração de relatórios
│   ├── dashboard/         # Dashboard e métricas
│   └── gestao_estoque/    # Settings
├── frontend/
│   ├── scss/
│   │   ├── core/
│   │   ├── produtos/
│   │   ├── movimentacoes/
│   │   └── variables.scss
│   └── js/
│       ├── dashboard.js
│       ├── produtos.js
│       └── vendors/
├── .venv/
├── .tool-versions         # asdf: Python 3.12.0 + Node.js 22.13.1
├── .nvmrc                 # NVM: Node.js 22
└── package.json
```

---

## 4 — Apps Django

### 4.1 core/
- Mixins de permissão
- Utilitários compartilhados
- Models base (TimeStampedModel)

### 4.2 autenticacao/
- CustomUser (estende AbstractUser)
- Grupos: Admin, Gestor, Operador
- Views: login, logout, recuperar_senha

### 4.3 produtos/
**Models:**
- `Product`: sku, name, description, category, unit, min_stock, current_stock, expiry_date
- `Category`: name, description
- `Unit`: name (ex: UN, KG, L)

### 4.4 movimentacoes/
**Models:**
- `InventoryMovement`: product, type (ENTRADA/SAIDA), quantity, document, user, timestamp
- `StockLocation`: name, description (para futuras expansões)

### 4.5 relatorios/
- Views para gerar relatórios
- Exportação PDF (WeasyPrint ou ReportLab)

### 4.6 dashboard/
- Métricas agregadas
- Alertas automáticos

---

## 5 — Exemplo de Model (Product)

```python
from django.db import models
from core.models import TimeStampedModel

class Product(TimeStampedModel):
    sku = models.CharField(max_length=64, unique=True, verbose_name="Código")
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    category = models.ForeignKey('produtos.Category', on_delete=models.PROTECT)
    unit = models.ForeignKey('produtos.Unit', on_delete=models.PROTECT)
    min_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.sku} — {self.name}"

    @property
    def stock_status(self):
        """Retorna: CRITICO, BAIXO, OK"""
        if self.current_stock == 0:
            return "CRITICO"
        elif self.current_stock <= self.min_stock:
            return "BAIXO"
        return "OK"
```

---

## 6 — Movimentações e Transações

* Usar `transaction.atomic()` para garantir consistência
* Atualizar `current_stock` automaticamente em `InventoryMovement.save()`
* Registrar usuário e timestamp em todas as movimentações

```python
from django.db import models, transaction
from core.models import TimeStampedModel

class InventoryMovement(TimeStampedModel):
    ENTRADA = 'ENTRADA'
    SAIDA = 'SAIDA'
    AJUSTE = 'AJUSTE'
    
    TYPE_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saída'),
        (AJUSTE, 'Ajuste'),
    ]
    
    product = models.ForeignKey('produtos.Product', on_delete=models.PROTECT)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    document = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey('auth.User', on_delete=models.PROTECT)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Atualizar estoque do produto
            if self.type == self.ENTRADA:
                self.product.current_stock += self.quantity
            elif self.type == self.SAIDA:
                self.product.current_stock -= self.quantity
            self.product.save()
            super().save(*args, **kwargs)
```

---

## 7 — Templates e Layout

### Base Template
```django
{# base.html #}
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Gestão de Estoque{% endblock %}</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar">
        <a href="{% url 'dashboard' %}">Dashboard</a>
        <a href="{% url 'produtos:list' %}">Produtos</a>
        <a href="{% url 'movimentacoes:list' %}">Movimentações</a>
        <a href="{% url 'relatorios:index' %}">Relatórios</a>
        <a href="{% url 'configuracoes' %}">Configurações</a>
    </nav>
    {% endif %}
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <script src="{% static 'js/bundle.js' %}"></script>
</body>
</html>
```

---

## 8 — SCSS: Organização

```
frontend/scss/
├── variables.scss         # Cores, espaçamentos
├── core/
│   ├── _layout.scss
│   ├── _components.scss
│   └── _navbar.scss
├── produtos/
│   ├── _produtos.scss
│   ├── _produtos_cores.scss
│   └── _produtos_cores_escuro.scss
└── dashboard/
    ├── _dashboard.scss
    └── _dashboard_cores.scss
```

**Regras:**
- SEMPRE usar variáveis de `variables.scss`
- Seguir BEM para classes
- Tema escuro em `[data-theme=dark] { ... }`

---

## 9 — JavaScript

* Alpine.js para interatividade leve (modals, dropdowns)
* Fetch API para AJAX
* Chart.js para gráficos do dashboard

```javascript
// produtos.js
export function initProductTable() {
    // Busca, filtros, edição inline
}
```

---

## 10 — Autenticação & Permissões

**Grupos:**
- `admin_estoque`: Todas as permissões
- `gestor`: Visualizar relatórios, gerenciar produtos
- `operador`: Apenas registrar movimentações

**Decorators:**
```python
from django.contrib.auth.decorators import permission_required

@permission_required('produtos.change_product')
def editar_produto(request, pk):
    ...
```

---

## 11 — Testes

* Cobertura mínima: **70%**
* Testar: CRUD de produtos, movimentações, cálculo de estoque, alertas

```python
from django.test import TestCase
from produtos.models import Product, Category, Unit

class ProductTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Alimentos")
        self.unit = Unit.objects.create(name="UN")
    
    def test_stock_status_critico(self):
        p = Product.objects.create(
            sku="ABC123",
            name="Teste",
            category=self.category,
            unit=self.unit,
            min_stock=10,
            current_stock=0
        )
        self.assertEqual(p.stock_status, "CRITICO")
```

---

## 12 — Comandos Úteis

```bash
# Ativar ambiente (ver .github/copilot-local.md)
source .venv/bin/activate

# Migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Testes
python3 manage.py test --keepdb
coverage run --source='.' manage.py test --keepdb
coverage report

# Frontend
npm install
npm run build

# Criar superuser
python3 manage.py createsuperuser
```

---

## 13 — Checklist para Novas Features

- [ ] Models criados no app correto
- [ ] Migrations geradas e aplicadas
- [ ] Testes com >= 70% coverage
- [ ] Templates responsivos
- [ ] SCSS seguindo padrão BEM
- [ ] JavaScript modular
- [ ] Permissões configuradas
- [ ] Documentação atualizada

---

## 14 — Próximos Passos

1. ✅ Implementar sistema de gestão de estoque
2. ⬜ Criar apps base (core, autenticacao, produtos)
3. ⬜ Implementar models e migrations
4. ⬜ Criar templates base e navbar
5. ⬜ Implementar dashboard
6. ⬜ CRUD de produtos
7. ⬜ Sistema de movimentações
8. ⬜ Relatórios
9. ⬜ Testes completos

---

## Princípios de Desenvolvimento

### 1. Código DRY
- ✅ Verificar código existente antes de criar novo
- ✅ Centralizar utilitários em `core/utils.py`
- ❌ NUNCA duplicar funções

### 2. Testes
- ✅ SEMPRE criar testes para novas features
- ✅ Cobertura mínima: 70%
- ✅ Rodar `python manage.py test <app> --keepdb`

### 3. Git/Commits
- Padrão: `tipo: descrição`
- Tipos: `feat`, `fix`, `refactor`, `test`, `docs`

### 4. Documentação
- ⚠️ **SEMPRE perguntar antes de gerar documentação**

---

## Observações Importantes

1. Este é um projeto de **gestão de estoque** baseado em Django + Wagtail
2. Não usa Wagtail CMS
3. Foco em simplicidade e performance
4. Django Admin para administração inicial
5. API REST opcional (DRF) para futuras integrações mobile
