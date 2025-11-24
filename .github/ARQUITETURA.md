# Arquitetura do Sistema ARES - Gestão de Estoque

## 📋 Visão Geral

Sistema Django + Wagtail profissional com arquitetura modular, componentes reutilizáveis e separação clara entre área pública e área restrita.

---

## 🏗️ Estrutura de Templates

### Base Templates

```
siteares/templates/
├── base.html                    # Template global principal (TODOS herdam deste)
├── base_public.html             # Base para área pública (sem login)
├── base_internal.html           # Base para área restrita (com login)
└── components/                  # Componentes de layout estrutural
    ├── header.html              # Cabeçalho com logo e identidade
    ├── top_menu.html            # Menu de navegação principal
    ├── footer.html              # Rodapé institucional
    └── breadcrumbs.html         # Navegação hierárquica
```

### Componentes Reutilizáveis

```
blocks/templates/
├── blocks/                      # Blocos Wagtail (StreamField)
│   ├── titulo.html
│   ├── banner.html
│   ├── carrossel_*.html
│   └── ...
└── include/                    # Componentes genéricos reutilizáveis
    ├── titulo.html             # Título de página versátil
    ├── card.html               # Cartão/box reutilizável
    ├── table.html              # Tabela padronizada
    ├── form_layout.html        # Layout de formulário
    ├── modal.html              # Modal reutilizável
    ├── alert.html              # Alertas e notificações
    └── pagination.html         # Paginação padronizada
```

---

## 🎯 Hierarquia de Templates

### Todos os templates devem seguir este padrão:

```django
{% extends "base.html" %}  {# ou base_public.html / base_internal.html #}

{% block title %}Meu Título{% endblock %}

{% block content %}
    <!-- Conteúdo específico da página -->
{% endblock %}

{% block extra_css %}
    <!-- CSS adicional se necessário -->
{% endblock %}

{% block extra_js %}
    <!-- JavaScript adicional se necessário -->
{% endblock %}
```

---

## 🔐 Área Pública vs Área Restrita

### Área Pública (base_public.html)
- **Acesso**: Sem necessidade de login
- **Estilo**: Loja/portal customizável via Wagtail
- **Páginas**:
  - Home pública (HomePage model)
  - Sobre nós
  - Produtos/Serviços
  - Notícias
  - Contato
  - Institucional

### Área Restrita (base_internal.html)
- **Acesso**: Exige login obrigatório
- **Estilo**: Interface corporativa/administrativa
- **Páginas**:
  - Dashboard
  - Gestão de Estoque
  - Produtos
  - Movimentações
  - Relatórios
  - Configurações
  - Usuários e Permissões

---

## 👥 Sistema de Perfis de Acesso (ACL)

### 3 Perfis Principais:

#### 1. Representante Legal (Administrador Máximo)
- Criado automaticamente ao criar empresa
- **Permissões**:
  - Ver tudo
  - Criar perfis de acesso
  - Criar e excluir usuários
  - Dar permissões a qualquer pessoa
  - Habilitar funcionalidades
  - Acesso total ao sistema

#### 2. Representante Delegado (Administrador Secundário)
- Criado pelo Representante Legal
- **Permissões**:
  - Tudo que o Representante Legal permite
  - **Exceto**: Excluir o próprio Representante Legal
  - Pode administrar Operadores
  - Pode habilitar recursos e tokens

#### 3. Operador (Usuário Operacional)
- Criado por Representante Legal ou Delegado
- **Permissões limitadas**:
  - Não pode liberar tokens ou permissões avançadas
  - Acesso específico por módulos:
    - Estoque (consulta/edição conforme permissão)
    - Relatórios (visualização)
    - Financeiro (se autorizado)
    - Suporte (tickets)
    - Consultas apenas

### Painel de Controle de Permissões
- Lista de usuários
- Edição granular de permissões
- Vinculação a papéis pré-definidos
- Função para reset automático de permissões
- Logs de auditoria

---

## 📦 Componentes Core a Criar

### 1. top_menu.html
```django
{# Menu superior com dados dinâmicos do Wagtail #}
- Navegação pública/interna
- Login/Logout
- Submenu expansível
- Responsivo (mobile hamburger)
```

### 2. header.html
```django
{# Cabeçalho visual #}
- Logo institucional
- Nome do sistema
- Menu secundário (perfil, notificações)
- Tema claro/escuro toggle
```

### 3. footer.html
```django
{# Rodapé institucional #}
- Informações de contato
- Links úteis
- Redes sociais
- Copyright e versão
```

### 4. breadcrumbs.html
```django
{# Navegação hierárquica #}
- Geração automática baseada em URLs
- Configurável via variável show_breadcrumbs
```

### 5. titulo.html (include/)
```django
{# Título de página versátil #}
- Título principal
- Subtítulo opcional
- Descrição opcional
- Ações contextuais (botões, filtros)
- Ícones Bootstrap Icons
- Níveis de heading customizáveis (h1, h2, h3)
```

### 6. card.html (include/)
```django
{# Cartão reutilizável #}
- Header com título e ações
- Body com conteúdo flexível
- Footer opcional
- Variantes: primary, success, warning, danger
```

### 7. table.html (include/)
```django
{# Tabela padronizada #}
- Cabeçalhos ordenáveis
- Paginação integrada
- Ações por linha
- Filtros contextuais
- Responsiva
```

### 8. form_layout.html (include/)
```django
{# Layout de formulário padronizado #}
- Campos com labels
- Mensagens de erro
- Validação inline
- Botões de ação
```

### 9. modal.html (include/)
```django
{# Modal reutilizável #}
- Título dinâmico
- Conteúdo flexível
- Botões de ação customizáveis
- Tamanhos: sm, md, lg, xl
```

### 10. alert.html (include/)
```django
{# Alertas e notificações #}
- Tipos: success, info, warning, danger
- Dispensável
- Ícones contextuais
```

---

## 🎨 Sistema de Temas (Futuro - FASE FINAL)

### Configuração via Wagtail Settings
- Tema claro (padrão)
- Tema escuro
- Paleta institucional customizável
- Logo por tema
- Cores primárias/secundárias

---

## 📊 Dashboard Interno

### Módulos Principais:
- **Resumo de Estoque**: Valor total, itens cadastrados
- **Alertas**: Estoque crítico, validade próxima
- **Gráficos**: Chart.js (produtos mais vendidos, movimentações)
- **Fluxos Recentes**: Últimas 10 movimentações
- **Widgets Configuráveis**: Drag-and-drop

---

## 📝 Sistema de Logs/Auditoria

### Rastreamento de:
- Movimentação de estoque (entradas/saídas)
- Usuários e permissões (criação, edição, exclusão)
- Ações sensíveis (exclusões, alterações críticas)
- Mudanças em páginas Wagtail (publish, unpublish)

### Interface de Consulta:
- Filtros por tipo, usuário, data
- Exportação para CSV/PDF
- Detalhamento completo de cada ação

---

## 🖼️ Sistema de Upload Padronizado

### Funcionalidades:
- Modal de upload reutilizável
- Validação de tipos (imagens, PDFs, etc.)
- Validação de tamanhos (max 10MB por padrão)
- Otimização automática de imagens
- Redimensionamento: original, fill (crop), max (proportional), min (fit)
- Integração com Wagtail Images
- Preview antes do upload

---

## 🔌 API REST Interna

### Tecnologias:
- Django REST Framework
- JWT Authentication para apps externos
- Documentação automática (Swagger/OpenAPI)
- Rate limiting (django-ratelimit)
- CORS configurado

### Endpoints Principais:
```
/api/v1/produtos/          # CRUD de produtos
/api/v1/movimentacoes/     # Movimentações de estoque
/api/v1/relatorios/        # Geração de relatórios
/api/v1/usuarios/          # Gestão de usuários
/api/v1/auth/              # Autenticação JWT
```

---

## 🗂️ Estrutura de Apps Django

```
projeto/
├── siteares/              # Configurações principais
├── core/                  # Funcionalidades compartilhadas
├── autenticacao/          # Login, logout, recuperação
├── produtos/              # CRUD de produtos
├── movimentacoes/         # Entradas e saídas
├── relatorios/            # Geração de relatórios
├── dashboard/             # Dashboard e métricas
├── usuarios/              # Gestão de usuários (ACL) - NOVO
├── auditoria/             # Sistema de logs - NOVO
├── api/                   # API REST - NOVO
├── home/                  # HomePage pública Wagtail
├── blocks/                # Blocos Wagtail reutilizáveis
└── search/                # Busca integrada
```

---

## 🧪 Testes e Qualidade

### Cobertura Mínima: 70%
- Testes unitários para models, views, forms
- Testes de integração para fluxos completos
- Testes de API com REST Framework
- Testes de permissões e ACL
- Testes de componentes reutilizáveis

### Ferramentas:
- pytest-django
- coverage
- factory_boy (fixtures)
- django-test-plus

---

## 📚 Documentação

### Documentação Técnica:
- Guia de instalação
- Estrutura de templates
- Sistema de componentes
- API Reference
- Guia de testes

### Documentação para Usuários:
- Manual do administrador
- Guia de permissões
- Tutorial de customização
- FAQ

---

## 🚀 Roadmap de Implementação

### FASE 1: Base Templates e Componentes Core ⏳
- Refatorar base.html
- Criar components/ e include/
- Implementar componentes essenciais

### FASE 2: Separação Público vs Restrito ⏸️
- Criar base_public.html e base_internal.html
- HomePage customizável via Wagtail
- Middleware de autenticação

### FASE 3: Sistema ACL ⏸️
- Modelos de perfis
- Painel de permissões
- Mixins e decorators

### FASE 4-8: Funcionalidades Avançadas ⏸️
- Dashboard avançado
- Logs e auditoria
- Upload padronizado
- API REST
- Testes e documentação

---

## 📖 Convenções e Padrões

### Templates:
- Sempre estender base.html ou variações
- Usar `{% include %}` para componentes
- Nunca colocar `<style>` ou `<script>` inline
- Usar variáveis de contexto descritivas

### CSS/SCSS:
- Nomenclatura BEM
- Variáveis em variables.scss
- Arquivos por app/componente
- Modo escuro em `[data-theme=dark]`

### JavaScript:
- Módulos em frontend/js/{app}/
- Exportar apenas funções globais necessárias
- Usar Alpine.js para interatividade leve

### Python:
- PEP 8 compliant
- Docstrings em todas as classes/funções
- Type hints quando aplicável
- Migrations sempre nomeadas descritivamente

---

**Última Atualização**: 19/11/2025
**Versão**: 2.0.0
**Status**: Em Reestruturação Ativa
