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
- ✅ SEMPRE verificar se já existe função/classe similar antes de criar nova
- ✅ Centralizar código reutilizável em arquivos de utilitários
- ✅ Utilitários de teste vão em `core/utils_test.py`
- ✅ Utilitários de produção vão em `core/utils.py` ou app específico
- ❌ NUNCA duplicar funções entre arquivos de teste

### 2. Testes
- ✅ SEMPRE criar testes para novas funcionalidades
- ✅ Usar `ensure_root_page()` de `core.utils_test` para setup de testes
- ✅ Rodar testes com: `python manage.py test <app> --keepdb`
- ✅ Executar coverage: `coverage run --source='.' manage.py test --keepdb`
- ✅ Normalizar locales nos testes: usar `get_supported_content_language_variant('pt-br')` retorna `'pt'`
- ✅ Inicializar `root.numchild = 0` em testes do Wagtail
- ✅ Sempre usar `root.refresh_from_db()` após operações de página
- ⚠️ **IMPORTANTE**: Ao modificar funcionalidades existentes, ATUALIZAR os testes para refletir o novo comportamento
- ❌ NUNCA alterar o código de produção para fazer os testes passarem - ajuste os testes para validar o comportamento correto
- ✅ Testes devem validar o comportamento atual do código, não o comportamento antigo
- ✅ Quando hooks/signals alteram dados automaticamente, os testes devem verificar os dados APÓS o processamento
- ✅ Usar métodos de teste apropriados:
  - `assertEqual()` para valores exatos
  - `assertIn()` para verificar se substring existe
  - `assertTrue()/assertFalse()` para condições booleanas
  - `assertRaises()` para verificar exceções
- ✅ Nomenclatura de testes: `test_<funcionalidade>_<cenario>` (ex: `test_titulo_dashboard_recorrente_com_produto`)
- ✅ Cobertura mínima: 70% de code coverage
- ✅ Testes de integração para fluxos completos (create → publish → verify)
- ✅ Testes unitários para funções helper isoladas

### 3. **Wagtail - Boas Práticas**
- ✅ Herdar de `Page` para páginas customizadas (já tem SEO, imagem destaque, descrição)
- ✅ Usar `StreamField` para conteúdo flexível, `TextField` para texto simples
- ✅ Migrations: usar `RenameField` para preservar dados (não `RemoveField` + `AddField`)
- ✅ Verificar conflitos de nomes de campos entre classe pai e filha
- ⚠️ Locale 'pt-br' é normalizado para 'pt' pelo Wagtail
- ⚠️ Treebeard requer `numchild` inicializado em páginas raiz

### 4. **Migrations**
- ✅ SEMPRE criar migrations para alterações de modelo
- ✅ Aplicar migrations após criação: `python manage.py migrate`
- ✅ Usar `RenameField` ao renomear campos (preserva dados)
- ✅ Verificar se migration foi aplicada antes de rodar testes
- ❌ NUNCA remover migrations já aplicadas

### 5. **Templates Django**
- ✅ Usar templatetags customizadas para lógica reutilizável
- ✅ Condicionar exibição de componentes com flags booleanas
- ✅ Usar `{% load static %}` no topo de todos os templates
- ❌ NUNCA colocar `<style>` ou `<script>` inline nos templates
- ❌ Não é necessário referenciar CSS/JS compilados: `{% static 'css/styles.css' %}`
- ✅ Exemplo: `{% if page.slideshow_imagens and page.images|length > 1 %}`
- ✅ Usar `{% load %}` para carregar templatetags necessárias
- ❌ NUNCA usar classes Bootstrap para cores (ex: `badge-primary`, `alert-info`)
- ✅ Criar classes personalizadas seguindo nomenclatura BEM

```django
{# ✅ CORRETO - Template limpo #}
{% extends "base.html" %}
{% load wagtailcore_tags %}
{% load static %}

{% block content %}
<div class="container my-4">

  {% include 'include/titulo.html' with titulo=page.introduction|default:"Contatos" bgClass='' %}

  <div class="contatos-grid">
    <div class="coluna-esquerda">
      {% for contato in coluna_1 %}
        {% include "contatos/contato_block.html" with content_block=contato %}
      {% endfor %}
    </div>

    <div class="coluna-direita">
      {% for contato in coluna_2 %}
        {% include "contatos/contato_block.html" with content_block=contato %}
      {% endfor %}
    </div>
  </div>
</div>
{% endblock content %}
```

### 6. Git/Commits
- ✅ Mensagens de commit seguem padrão: `tipo: descrição`
  - `feat:` nova funcionalidade
  - `fix:` correção de bug
  - `refactor:` refatoração de código
  - `test:` adição/modificação de testes
  - `docs:` documentação
- ✅ Corpo do commit lista alterações detalhadas com marcadores
- ✅ Mencionar número de testes passando no commit quando relevante

### 7. Documentação
- ⚠️ **SEMPRE perguntar antes de gerar documentação**

---

### 8. **CSS/SCSS - Organização e Padrões**

#### 8.1. Organização por App
- ✅ SEMPRE criar arquivos SCSS dentro da pasta do app correspondente
- ✅ Estrutura: `frontend/scss/{nome_do_app}/`
- ✅ Apenas componentes globais vão em `frontend/scss/core/`
- ❌ NÃO usar pasta `components/` genérica

```
frontend/scss/
├── produtos/           # App produtos
│   ├── index.scss     # Importa todos os arquivos do app
│   ├── produtos.scss
│   └── produtos_escuro.scss
├── dashboard/         # App dashboard
├── core/             # Apenas componentes globais
└── variables.scss    # Variáveis globais de cor
```

#### 8.2. Sistema de Temas

**Temas Disponíveis:**

1. **Theme ARES (Vermelho)**
   - Modo Claro: Vermelho + Branco
   - Modo Escuro: Vermelho + Preto

2. **Theme ATHENA (Azul)**
   - Modo Claro: Azul + Branco
   - Modo Escuro: Azul + Preto

**Estrutura de Arquivos por Componente:**
- ✅ `componente.scss` - Layout, estrutura, espaçamentos (SEM cores hardcoded)
- ✅ `componente_escuro.scss` - Variações para modo escuro

**Importante:** No arquivo `_escuro.scss`, SEMPRE envolver as regras com `[data-theme=dark] { }`

```scss
// ❌ ERRADO - componente_escuro.scss
.meu-componente {
  background-color: $color-dark-theme-bg;
}

// ✅ CORRETO - componente_escuro.scss
[data-theme=dark] {
  .meu-componente {
    background-color: $color-dark-theme-bg;
  }
}
```

#### 8.3. Uso de Variáveis CSS Custom Properties
- ❌ NUNCA usar cores diretas: `#333`, `blue`, `rgba(...)`
- ✅ SEMPRE usar CSS custom properties de `variables.scss`:
  - `$color-primary` - Cor primária do tema atual
  - `$color-primary-hover` - Cor de hover
  - `$color-bg` - Background principal
  - `$color-text` - Cor de texto
  - `$color-border` - Cor de bordas
```scss
// ❌ ERRADO
.meu-componente {
  background-color: #c62828;
  color: #fff;
  border: 1px solid #ddd;
}

// ✅ CORRETO
.meu-componente {
  background-color: variables.$color-primary;
  color: variables.$color-text;
  border: 1px solid variables.$color-border;
}
```
#### 6.4 Criação de Novas Cores
- Se cor não existe em `variables.scss`:
  1. Adicionar variável em `variables.scss` com nome semântico
  2. Criar versão escura se necessário
  3. Usar a variável nos arquivos de cores

#### 8.5. Nomenclatura BEM
- ✅ Usar padrão BEM (Block Element Modifier):
  - Bloco: `.produtos-page`
  - Elemento: `.produtos-page__card`, `.produtos-page__title`
  - Modificador: `.produtos-page__badge--critical`

#### 8.6. Imports no index.scss
```scss
// frontend/scss/produtos/index.scss
@use './produtos.scss';
@use './produtos_escuro.scss';
```

### 9. **Acessibilidade (A11y)**

**Padrões a seguir:**
- WCAG 2.1 Level AA: https://www.w3.org/WAI/WCAG21/quickref/
- Axe DevTools Rules: https://dequeuniversity.com/rules/axe/4.10

**Ferramentas de validação:**
- Axe DevTools (extensão do navegador)
- WAVE (Web Accessibility Evaluation Tool)
- Lighthouse (Chrome DevTools)

#### 9.1 HTML Semântico
- ✅ Usar elementos HTML semânticos apropriados (WCAG 1.3.1 - Info and Relationships)
- ❌ NUNCA usar `<strong>` ou `<b>` em parágrafos como se fossem headings
- ✅ Usar hierarquia correta de headings (h1 → h2 → h3...) sem pular níveis
- ✅ Usar `<dl>`, `<dt>`, `<dd>` para listas de definição/dados chave-valor
- ✅ Usar `<button>` para ações, `<a>` para navegação
- ✅ Elementos de formulário devem ter labels associados (`<label for="id">`)

```html
<!-- ❌ ERRADO - strong como heading -->
<div>
  <strong>Autoridade:</strong> Nome da autoridade
</div>

<!-- ✅ CORRETO - elementos semânticos -->
<dl>
  <dt>Autoridade:</dt>
  <dd>Nome da autoridade</dd>
</dl>
```

## 9.2 Contraste de Cores (WCAG 1.4.3)
- ✅ Garantir contraste mínimo WCAG AA:
  - Texto normal: 4.5:1
  - Texto grande (18pt+ ou 14pt+ negrito): 3:1
- ✅ Testar em ambos os temas (claro e escuro)
- ✅ Texto sobre fundos coloridos deve ter contraste adequado
- ✅ Usar ferramentas como WebAIM Contrast Checker

#### 9.3 Estrutura e Navegação
- ✅ Landmarks ARIA quando apropriado (`main`, `nav`, `aside`, `header`, `footer`)
- ✅ Labels descritivos em formulários (WCAG 3.3.2)
- ✅ Alternativas textuais para imagens (`alt`) - WCAG 1.1.1
- ✅ Foco visível em elementos interativos (WCAG 2.4.7)
- ✅ Links descritivos - evitar "clique aqui" (WCAG 2.4.4)
- ✅ Skip links para navegação rápida

#### 9.4 Responsividade e Zoom (WCAG 1.4.4, 1.4.10)
- ✅ Testar em diferentes tamanhos de tela
- ✅ Garantir que texto possa ser ampliado até 200% sem perda de conteúdo
- ✅ Evitar scroll horizontal em dispositivos móveis
- ✅ Viewport não deve bloquear zoom: `<meta name="viewport" content="width=device-width, initial-scale=1">`

#### 9.5 Interatividade
- ✅ Navegação por teclado funcionando (Tab, Enter, Setas)
- ✅ Ordem de foco lógica (WCAG 2.4.3)
- ✅ Modais devem capturar foco (focus trap)
- ✅ Estados de erro claramente identificados (WCAG 3.3.1)

### 10. **JavaScript - Organização**
- ✅ Criar módulos JS dentro de `frontend/js/{nome_do_app}/`
- ✅ Exportar funções globais apenas quando necessário: `window.minhaFuncao = ...`
- ✅ Importar todos os módulos no `frontend/js/index.js`
- ❌ NUNCA colocar JavaScript inline nos templates HTML

```javascript
// frontend/js/produtos/produtos.js
document.addEventListener('DOMContentLoaded', function() {
    // Código do módulo
});

// Função global se necessário
window.exportProducts = function() {
    // Implementação
};
```

---

## 11. **Arquitetura de Templates - Padrão Modular e Reutilizável**

### 11.1. Estrutura Base de Templates

O sistema utiliza uma arquitetura de templates modular com componentes reutilizáveis:

```
siteares/templates/
├── base.html                    # Template global principal
├── base_authenticated.html      # Base para área restrita (futura)
├── base_public.html            # Base para área pública (futura)
└── components/                 # Componentes de layout
    ├── header.html             # Cabeçalho com logo e identidade
    ├── top_menu.html           # Menu de navegação principal
    ├── footer.html             # Rodapé institucional
    └── breadcrumbs.html        # Navegação hierárquica

blocks/templates/
├── blocks/                      # Blocos Wagtail (StreamField)
│   ├── titulo.html             # Bloco de título Wagtail
│   ├── banner.html             # Banner rotativo
│   ├── carrossel_*.html        # Carrosséis diversos
│   └── ...                     # Outros blocos Wagtail
└── include/                    # Componentes reutilizáveis genéricos
    ├── titulo.html             # Título de página versátil
    ├── card.html               # Cartão/box reutilizável (futuro)
    ├── table.html              # Tabela padronizada (futuro)
    └── form_layout.html        # Layout de formulário (futuro)
```

### 11.2. base.html - Template Global Principal

**Todos os templates devem estender `base.html`:**

```django
{% extends "base.html" %}
{% block content %}
    <!-- Conteúdo específico da página -->
{% endblock %}
```

**Estrutura do base.html:**
- ✅ `{% load static wagtailcore_tags %}` no topo
- ✅ Metadados SEO (title, description, og:tags)
- ✅ CSS global via `{% static 'css/styles.*.css' %}`
- ✅ `{% include 'components/header.html' %}`
- ✅ `{% include 'components/top_menu.html' %}`
- ✅ `{% include 'components/breadcrumbs.html' %}` (condicional)
- ✅ `{% include 'components/titulo.html' %}` (condicional)
- ✅ `{% block content %}{% endblock %}`
- ✅ `{% include 'components/footer.html' %}`
- ✅ JS global via `{% static 'js/main.js' %}`
- ✅ `{% block extra_js %}{% endblock %}` para JS específico

### 11.3. Componentes Reutilizáveis

#### 11.3.1. header.html
- Logo do sistema
- Nome da aplicação
- Informações de usuário logado
- Atalhos principais

#### 11.3.2. top_menu.html
- Menu de navegação principal
- Suporte a submenus
- Indicador de página ativa
- Responsivo (mobile hamburger)
- Dados dinâmicos do Wagtail quando disponível

#### 11.3.3. footer.html
- Informações institucionais
- Links úteis
- Copyright e versão
- Redes sociais (opcional)

#### 11.3.4. breadcrumbs.html
- Navegação hierárquica
- Geração automática baseada em URLs
- Pode ser ocultado via variável `show_breadcrumbs`

#### 11.3.5. titulo.html (em blocks/templates/include/)
- Título principal da página
- Subtítulo opcional
- Descrição opcional
- Ações contextuais (botões, filtros)
- Suporte a ícones Bootstrap Icons
- Compatível com blocos Wagtail (bgClass, remover_svg, centralizado)
- Níveis de heading customizáveis (h1, h2, h3)

**Uso:**
```django
{% include 'include/titulo.html' with titulo="Produtos" subtitulo="Gerenciar estoque" icon="box-seam" show_actions=True %}

{# Uso Wagtail (compatibilidade) #}
{% include 'include/titulo.html' with titulo=self.titulo bgClass=self.corBackground centralizado=True %}
```

#### 11.3.6. Componentes Detectados Automaticamente

O sistema deve identificar padrões repetidos e sugerir novos componentes:
- ✅ Cards/boxes para exibição de dados
- ✅ Tabelas com paginação e ordenação
- ✅ Formulários com layout padrão
- ✅ Modais reutilizáveis
- ✅ Alertas e notificações
- ✅ Listas de atalhos/widgets
- ✅ Painéis colapsáveis

### 11.4. Separação: Área Pública vs. Área Restrita

#### 11.4.1. Área Pública (Futura - Não Implementada)
- Home pública customizável via Wagtail
- Estilo loja/portal
- Sem necessidade de login
- Banner rotativo, destaques, notícias
- Listagem de produtos/serviços
- Rodapé configurável

#### 11.4.2. Área Restrita (Atual)
- **TODO O SISTEMA ATUAL É ÁREA RESTRITA**
- Exige login obrigatório
- Interface corporativa/funcional
- Dashboard administrativo
- Gestão de estoque, produtos, movimentações
- Relatórios e configurações

### 11.5. Organização de Componentes Reutilizáveis

**Onde colocar cada tipo de componente:**

#### 11.5.1. `siteares/templates/components/`
Componentes de **layout estrutural** (usados no base.html):
- ✅ header.html (cabeçalho principal)
- ✅ top_menu.html (menu de navegação)
- ✅ footer.html (rodapé)
- ✅ breadcrumbs.html (navegação hierárquica)

#### 11.5.2. `blocks/templates/include/`
Componentes **genéricos reutilizáveis** (usados em qualquer página):
- ✅ titulo.html (título de página versátil)
- ⏳ card.html (cartões/boxes)
- ⏳ table.html (tabelas padronizadas)
- ⏳ form_layout.html (layouts de formulário)
- ⏳ modal.html (modais reutilizáveis)
- ⏳ alert.html (alertas e notificações)

#### 11.5.3. `blocks/templates/blocks/`
Blocos **específicos do Wagtail StreamField**:
- ✅ titulo.html (wrapper para include/titulo.html)
- ✅ banner.html, carrossel_*.html
- ✅ Outros blocos de conteúdo Wagtail

**Regra de ouro:** Se o componente pode ser usado em qualquer página (Django ou Wagtail), vai para `blocks/templates/include/`. Se é estrutura de layout, vai para `siteares/templates/components/`.

### 11.6. Regras de Templates

- ✅ **SEMPRE** estender `base.html` ou variações (`base_authenticated.html`)
- ✅ **NUNCA** colocar `<style>` ou `<script>` inline nos templates
- ✅ **SEMPRE** usar `{% include 'components/...' %}` para componentes de layout
- ✅ **SEMPRE** usar `{% include 'include/...' %}` para componentes genéricos
- ✅ **SEMPRE** usar `{% load static %}` quando referenciar arquivos estáticos
- ✅ CSS/JS compilados são referenciados automaticamente pelo base.html
- ✅ Usar `{% block extra_css %}` e `{% block extra_js %}` para arquivos específicos
- ✅ Passar variáveis para componentes via `with`: `{% include 'comp.html' with var=value %}`
- ✅ Usar `{% if %}` para condicionar exibição de componentes
- ❌ **NUNCA** duplicar header, footer ou menu entre templates
- ❌ **NUNCA** usar classes Bootstrap para cores (criar classes personalizadas BEM)
- ❌ **NUNCA** incluir breadcrumbs manualmente (já está no base.html)
- ✅ **page_header** é opcional - cada página decide se mostra título ou não
- ✅ Para **Wagtail**: usar StreamField para conteúdo customizável pelo cliente
- ✅ **Título de página** deve ser definido em `{% block page_header %}` quando necessário

---

## 12. **Plano de Remodelação do Sistema (Roadmap)**

### FASE 1: Fundação - Templates Base e Componentes ✅ EM ANDAMENTO
**Objetivo:** Criar estrutura modular e reutilizável de templates

- [ ] Criar `sitepadrao/templates/base.html` unificado
- [ ] Criar `sitepadrao/templates/components/header.html`
- [ ] Criar `sitepadrao/templates/components/top_menu.html`
- [ ] Criar `sitepadrao/templates/components/footer.html`
- [ ] Criar `sitepadrao/templates/components/breadcrumbs.html`
- [ ] Criar `sitepadrao/templates/components/titulo.html`
- [ ] Refatorar templates existentes para usar `base.html` e componentes
- [ ] Criar componentes adicionais conforme padrões detectados (card, table, form_layout)
- [ ] Testar em todas as páginas atuais (autenticacao, dashboard, produtos, movimentacoes, relatorios)
- [ ] Validar responsividade e acessibilidade

**Prioridade:** ALTA - Base para tudo  
**Status:** Iniciando agora

### FASE 2: Separação Público vs. Restrito ⏳ FUTURO
**Objetivo:** Criar área pública (home estilo loja) separada da área restrita

- [ ] Criar `sitepadrao/templates/base_public.html`
- [ ] Criar `sitepadrao/templates/base_authenticated.html`
- [ ] Criar modelo Wagtail `HomePage` para home pública customizável
- [ ] Criar componentes específicos para área pública (banner rotativo, destaques, notícias)
- [ ] Configurar URLs públicas vs. restritas
- [ ] Implementar middleware de autenticação para área restrita
- [ ] Criar menu diferenciado para área pública
- [ ] Adaptar dashboard interno para `base_authenticated.html`
- [ ] Testes de navegação entre áreas

**Prioridade:** MÉDIA  
**Status:** Aguardando FASE 1

### FASE 3: Sistema ACL - Controle de Acesso Robusto ⏳ FUTURO
**Objetivo:** Implementar 3 perfis de acesso (Representante Legal, Delegado, Operador)

- [ ] Criar modelos de perfis em `core/models.py`:
  - `RepresentanteLegal` (administrador máximo)
  - `RepresentanteDelegado` (administrador secundário)
  - `Operador` (usuário operacional)
- [ ] Implementar sistema de permissões granulares por módulo
- [ ] Criar painel de gerenciamento de usuários (CRUD completo)
- [ ] Implementar mixins e decorators de permissão por perfil
- [ ] Criar sistema de logs de auditoria (quem fez o quê, quando)
- [ ] Interface para edição granular de permissões
- [ ] Vinculação a papéis pré-definidos
- [ ] Função de reset automático de permissões
- [ ] Testes de segurança e edge cases
- [ ] Documentação do sistema de permissões

**Prioridade:** BAIXA (pode vir depois)  
**Status:** Aguardando FASE 2

### FASE 4: Funcionalidades Avançadas ⏳ FUTURO
**Objetivo:** Dashboard avançado, logs, upload, API

- [ ] **Dashboard Interno Avançado:**
  - Gráficos com Chart.js
  - Resumo de estoque em tempo real
  - Alertas de itens em baixa
  - Fluxos recentes de movimentações
  - Widgets configuráveis
  
- [ ] **Sistema de Logs/Auditoria:**
  - Movimentação de estoque
  - Mudanças de usuários e permissões
  - Ações sensíveis (exclusões, alterações críticas)
  - Mudanças em páginas Wagtail
  - Interface de consulta de logs
  
- [ ] **Sistema de Upload Padronizado:**
  - Modal de upload reutilizável
  - Validação de tipos e tamanhos
  - Otimização automática de imagens
  - Redimensionamento (original, fill, max, min)
  - Integração com Wagtail Images
  
- [ ] **Personalização de Aparência:**
  - Configuração de paleta via Wagtail Settings
  - Temas claro/escuro por empresa (multi-tenant)
  - Logo customizável
  
- [ ] **API REST Interna:**
  - Endpoints para ações internas (Django REST Framework)
  - Autenticação JWT para apps externos
  - Documentação automática (Swagger/OpenAPI)
  - Rate limiting e segurança

**Prioridade:** BAIXA  
**Status:** Aguardando FASE 3

---

## 📐 **REESTRUTURAÇÃO ARQUITETURAL EM ANDAMENTO**

### Status Atual: FASE 1 - Base Templates e Componentes Core ⚙️

**O que foi implementado até agora:**

1. ✅ **Documento de Arquitetura**: Criado `.github/ARQUITETURA.md` com visão completa do sistema
2. ✅ **Estrutura de Components**: Criada pasta `siteares/templates/components/`
3. ✅ **Reorganização de Templates**:
   - `header.html` → `components/header.html`
   - `footer.html` → `components/footer.html`
   - `breadcrumb.html` → `components/breadcrumbs.html`
4. ✅ **Novo base.html Modular**: Refatorado com blocos claros:
   - `{% block header %}` - Cabeçalho e menu
   - `{% block breadcrumbs %}` - Navegação hierárquica
   - `{% block page_header %}` - Título opcional por página
   - `{% block content %}` - Conteúdo principal
   - `{% block footer %}` - Rodapé
5. ✅ **Roadmap de 8 Fases**: Definido em `manage_todo_list`

**Próximos Passos na FASE 1:**
- [ ] Criar componentes em `blocks/templates/include/`:
  - `titulo.html` (título de página versátil)
  - `card.html` (cartões reutilizáveis)
  - `table.html` (tabelas padronizadas)
  - `form_layout.html` (layouts de formulário)
  - `modal.html` (modais reutilizáveis)
  - `alert.html` (alertas e notificações)
- [ ] Refatorar páginas existentes para usar novos componentes
- [ ] Validar que todos os templates funcionam com nova estrutura

**IMPORTANTE**: 
- TODOS os templates devem estender `base.html`
- Use `{% include 'components/...' %}` para componentes de layout
- Use `{% include 'include/...' %}` para componentes genéricos
- **Temas ficam para ÚLTIMA FASE** (não priorizar agora)

---

## Observações Importantes

1. **SEMPRE** verificar duplicação de código antes de criar nova função
2. **NUNCA** criar documentação markdown sem perguntar ao usuário
3. **SEMPRE** criar testes para novas funcionalidades
4. **SEMPRE** usar `ensure_root_page()` de `core.utils_test` em testes
5. **SEMPRE** normalizar locale 'pt-br' → 'pt' em testes Wagtail
6. **CRÍTICO**: Limpar páginas filhas no `setUpTestData` quando usar `ensure_root_page()`
7. **SEMPRE** fazer `root.refresh_from_db()` após operações de página
8. Usar `RenameField` para preservar dados em migrations
9. Verificar conflitos de nomes entre classes pai/filho
10. Perguntar sobre documentação antes de gerar
11. **SEMPRE** perguntar sobre comandos de ambiente antes de executar pela primeira vez
12. **CRÍTICO**: Re-publicar páginas após adicionar tags/relacionamentos para queries `.live()`
13. **CRÍTICO**: Criar `Site` no `setUpTestData` quando testes renderizam templates
14. **CRÍTICO**: Criar `Collection.add_root()` no `setUpTestData` quando testes usam Image/Document
15. **CRÍTICO**: Testar sem `--keepdb` antes de push para CI/CD (simular banco limpo)
16. **CRÍTICO**: Settings de teste devem usar backends simples (não ManifestStaticFilesStorage)
17. **Hooks do Wagtail**: Manter verificações condicionais simples e explícitas, evitar lógica complexa de "prevenção"