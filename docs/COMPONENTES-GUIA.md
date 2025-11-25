# 📦 Guia de Componentes Reutilizáveis

Biblioteca completa de componentes HTML reutilizáveis para o Sistema ARES.

## 📍 Localização

Todos os componentes estão em: `siteares/templates/components/`

## 🎨 Componentes Disponíveis

### 1. top_menu.html - Menu Superior Dinâmico

Menu de navegação responsivo integrado com Wagtail e sistema de perfis.

**Uso:**
```django
{% include 'components/top_menu.html' %}
```

**Recursos:**
- Menu dinâmico do Wagtail (páginas configuráveis)
- Links do sistema interno (Dashboard, Produtos, etc.)
- Controle de acesso por perfil
- Dropdown de usuário com badge de perfil
- Responsivo com Bootstrap 5

---

### 2. titulo.html - Título de Página Padronizado

Cabeçalho de página com ícone, título, subtítulo e ações.

**Uso:**
```django
{% include 'components/titulo.html' with 
    title='Produtos' 
    subtitle='Gerenciar catálogo de produtos'
    icon='bi-box'
    show_back=True
%}
```

**Parâmetros:**
- `title` - Título principal (obrigatório)
- `subtitle` - Subtítulo opcional
- `icon` - Ícone Bootstrap Icons (ex: 'bi-box')
- `show_back` - Mostra botão voltar
- `back_url` - URL customizada para voltar
- `actions` - HTML de botões de ação

---

### 3. card.html - Cartão Reutilizável

Card Bootstrap flexível com header, body, footer e imagem.

**Uso:**
```django
{% include 'components/card.html' with 
    title='Estatísticas'
    icon='bi-graph-up'
    body_content='<p>Conteúdo aqui</p>'
    shadow=True
    hover=True
%}
```

**Parâmetros:**
- `title` - Título do card
- `icon` - Ícone no header
- `header` - HTML customizado para header
- `body_content` - Conteúdo HTML do body
- `footer_content` - Conteúdo HTML do footer
- `image_url` - URL da imagem
- `shadow` - Adiciona sombra
- `hover` - Efeito hover
- `card_class`, `header_class`, `body_class`, `footer_class` - Classes CSS customizadas

---

### 4. modal.html - Modal Reutilizável

Modal Bootstrap configurável com header, body e footer.

**Uso:**
```django
{% include 'components/modal.html' with 
    modal_id='deleteModal'
    title='Confirmar Exclusão'
    icon='bi-trash'
    body='<p>Tem certeza que deseja excluir?</p>'
    modal_size='sm'
    modal_centered=True
    show_footer=True
    confirm_text='Excluir'
    confirm_action='deleteItem()'
%}
```

**Parâmetros:**
- `modal_id` - ID único do modal (obrigatório)
- `title` - Título do modal
- `icon` - Ícone no título
- `body` - Conteúdo HTML
- `modal_size` - Tamanho: 'sm', 'lg', 'xl', 'fullscreen'
- `modal_centered` - Centraliza verticalmente
- `modal_scrollable` - Body com scroll
- `show_footer` - Exibe footer
- `cancel_text` - Texto do botão cancelar
- `confirm_text` - Texto do botão confirmar
- `confirm_action` - JavaScript do botão confirmar

---

### 5. alert.html - Alertas/Mensagens

Alertas contextuais com ícones e ações.

**Uso:**
```django
{% include 'components/alert.html' with 
    type='success'
    title='Sucesso!'
    message='Produto salvo com sucesso.'
    dismissible=True
%}
```

**Tipos:** `success`, `danger`, `warning`, `info`, `primary`, `secondary`

**Parâmetros:**
- `type` - Tipo do alert (define cor/ícone)
- `title` - Título opcional
- `message` - Mensagem principal
- `details` - Texto de detalhes
- `icon` - Ícone customizado
- `dismissible` - Permite fechar
- `action_url` - URL de ação
- `action_text` - Texto do link de ação

---

### 6. form_field.html - Campo de Formulário

Campo de formulário Django com validação e estilos Bootstrap.

**Uso:**
```django
{% include 'components/form_field.html' with field=form.nome %}

{% include 'components/form_field.html' with 
    field=form.preco 
    prepend_text='R$'
    placeholder='0,00'
%}
```

**Parâmetros:**
- `field` - Campo do Django Form (obrigatório)
- `hide_label` - Oculta label
- `placeholder` - Placeholder do input
- `prepend_text` - Texto antes do input
- `append_text` - Texto depois do input
- `rows` - Linhas do textarea (padrão: 3)
- `field_class` - Classes CSS adicionais
- `custom_help` - Texto de ajuda customizado
- `help_text_inline` - Ajuda inline no label

**Suporta:**
- Text inputs, textareas, selects, checkboxes
- Validação com mensagens de erro
- Campos obrigatórios (asterisco automático)
- Input groups (prepend/append)

---

### 7. button.html - Botão Padronizado

Botões e links estilizados como botões.

**Uso:**
```django
{% include 'components/button.html' with 
    text='Salvar'
    icon='bi-save'
    style='primary'
    button_type='submit'
%}

{% include 'components/button.html' with 
    text='Ver Produto'
    icon='bi-eye'
    href='/produtos/1/'
    style='info'
%}
```

**Parâmetros:**
- `text` - Texto do botão
- `icon` - Ícone Bootstrap Icons
- `style` - Estilo: 'primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'
- `outline` - Versão outline
- `size` - Tamanho: 'sm', 'lg'
- `button_type` - Tipo: 'button', 'submit', 'reset'
- `href` - Para links (botão vira <a>)
- `onclick` - JavaScript onclick
- `disabled` - Desabilita botão
- `data_attrs` - Dicionário de data attributes

---

### 8. table.html - Tabela Responsiva

Tabela completa com ordenação, seleção e ações.

**Uso:**
```django
{% include 'components/table.html' with 
    headers=headers
    rows=rows
    striped=True
    hover=True
    selectable=True
    actions=True
%}
```

**Estrutura de dados:**

```python
# View
headers = [
    {'label': 'ID', 'width': '80px', 'sortable': True},
    {'label': 'Nome', 'sortable': True},
    {'label': 'Status', 'class': 'text-center'},
]

rows = [
    {
        'id': 1,
        'cells': [
            {'value': '#001'},
            {'value': 'Produto A'},
            {'value': '<span class="badge bg-success">Ativo</span>'},
        ],
        'can_edit': True,
        'can_view': True,
        'can_delete': True,
        'edit_url': '/produtos/1/edit/',
        'view_url': '/produtos/1/',
        'delete_url': '/produtos/1/delete/',
        'name': 'Produto A',
    }
]
```

**Parâmetros:**
- `headers` - Lista de cabeçalhos
- `rows` - Lista de linhas
- `striped` - Linhas zebradas
- `bordered` - Bordas
- `hover` - Efeito hover
- `small` - Versão compacta
- `selectable` - Checkboxes de seleção
- `actions` - Coluna de ações (editar/ver/excluir)
- `empty_message` - Mensagem quando vazio

---

### 9. panel.html - Painel Colapsável

Painéis expansíveis (accordions) com conteúdo colapsável.

**Uso:**
```django
{% include 'components/panel.html' with 
    panel_id='panel1'
    title='Informações Avançadas'
    icon='bi-gear'
    content='<p>Conteúdo do painel</p>'
    collapsible=True
    expanded=True
%}
```

**Para Accordion (múltiplos painéis):**
```django
<div id="accordionExample">
    {% include 'components/panel.html' with 
        panel_id='panel1'
        parent_id='accordionExample'
        title='Seção 1'
        content='Conteúdo 1'
        collapsible=True
        expanded=True
    %}
    
    {% include 'components/panel.html' with 
        panel_id='panel2'
        parent_id='accordionExample'
        title='Seção 2'
        content='Conteúdo 2'
        collapsible=True
    %}
</div>
```

**Parâmetros:**
- `panel_id` - ID único (obrigatório se collapsible)
- `parent_id` - ID do accordion pai (para acordeões)
- `title` - Título do painel
- `icon` - Ícone no título
- `content` - Conteúdo HTML
- `footer` - Rodapé HTML
- `collapsible` - Se é colapsável
- `expanded` - Se inicia expandido

---

## 🎯 Boas Práticas

### 1. Sempre use os componentes ao invés de HTML repetido

❌ **Evite:**
```django
<div class="alert alert-success">
    <i class="bi bi-check"></i> Sucesso!
</div>
```

✅ **Prefira:**
```django
{% include 'components/alert.html' with type='success' message='Sucesso!' %}
```

### 2. Passe parâmetros nomeados para clareza

```django
{% include 'components/button.html' with 
    text='Salvar' 
    style='primary' 
    icon='bi-save'
%}
```

### 3. Use `|safe` quando passar HTML

```django
{% include 'components/card.html' with 
    body_content=my_html_content|safe 
%}
```

### 4. Combine componentes para layouts complexos

```django
{% include 'components/card.html' with title='Formulário' %}
    <form method="post">
        {% csrf_token %}
        {% for field in form %}
            {% include 'components/form_field.html' with field=field %}
        {% endfor %}
        {% include 'components/button.html' with text='Salvar' button_type='submit' %}
    </form>
{% endinclude %}
```

---

## 🔧 Customização

Todos os componentes aceitam classes CSS customizadas:

```django
{% include 'components/alert.html' with 
    type='info'
    message='Mensagem'
    custom_class='my-custom-class'
%}
```

Você pode também sobrescrever estilos criando CSS específico no seu template ou em arquivos SCSS.

---

## 📚 Exemplos Práticos

### Página de Listagem Completa

```django
{% extends 'base.html' %}
{% load perfil_tags %}

{% block content %}
    {% include 'components/titulo.html' with 
        title='Produtos'
        subtitle='Gerenciar catálogo de produtos'
        icon='bi-box'
    %}
    
    {% if messages %}
        {% for message in messages %}
            {% include 'components/alert.html' with 
                type=message.tags
                message=message
                dismissible=True
            %}
        {% endfor %}
    {% endif %}
    
    {% include 'components/card.html' with title='Lista de Produtos' %}
        <div class="mb-3">
            {% include 'components/button.html' with 
                text='Novo Produto'
                icon='bi-plus'
                style='success'
                href='/produtos/novo/'
            %}
        </div>
        
        {% include 'components/table.html' with 
            headers=headers
            rows=rows
            striped=True
            hover=True
            actions=True
        %}
    {% endinclude %}
{% endblock %}
```

### Formulário Completo

```django
{% extends 'base.html' %}

{% block content %}
    {% include 'components/titulo.html' with 
        title='Novo Produto'
        icon='bi-plus-circle'
        show_back=True
    %}
    
    {% include 'components/card.html' with title='Dados do Produto' %}
        <form method="post" enctype="multipart/form-data">
            {% csrf_token %}
            
            <div class="row">
                <div class="col-md-8">
                    {% include 'components/form_field.html' with field=form.nome %}
                </div>
                <div class="col-md-4">
                    {% include 'components/form_field.html' with 
                        field=form.preco 
                        prepend_text='R$'
                    %}
                </div>
            </div>
            
            {% include 'components/form_field.html' with 
                field=form.descricao 
                rows=5
            %}
            
            <div class="d-flex gap-2">
                {% include 'components/button.html' with 
                    text='Salvar'
                    button_type='submit'
                    style='primary'
                    icon='bi-save'
                %}
                
                {% include 'components/button.html' with 
                    text='Cancelar'
                    href='/produtos/'
                    style='secondary'
                    outline=True
                %}
            </div>
        </form>
    {% endinclude %}
{% endblock %}
```

---

## 🎨 Ícones Bootstrap Icons

Todos os componentes suportam ícones do Bootstrap Icons. Alguns ícones úteis:

- `bi-box` - Produtos
- `bi-arrow-left-right` - Movimentações
- `bi-file-earmark-text` - Relatórios
- `bi-speedometer2` - Dashboard
- `bi-person` - Usuário
- `bi-gear` - Configurações
- `bi-plus` - Adicionar
- `bi-pencil` - Editar
- `bi-trash` - Excluir
- `bi-eye` - Visualizar
- `bi-save` - Salvar
- `bi-x` - Cancelar

Veja todos em: https://icons.getbootstrap.com/

---

**Última atualização:** 25/11/2025
