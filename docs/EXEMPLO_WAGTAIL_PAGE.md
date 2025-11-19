# Exemplo: Página Wagtail Customizável

## Model (models.py)
```python
from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail import blocks as wagtail_blocks
from blocks.blocks import TituloBlock, BannerBlock, CardBlock

class DashboardPage(Page):
    """
    Página de Dashboard customizável via Wagtail Admin.
    Cliente pode adicionar/remover/reordenar blocos.
    """
    
    # Conteúdo customizável via StreamField
    body = StreamField([
        ('titulo', TituloBlock()),
        ('banner', BannerBlock()),
        ('card_metricas', CardBlock()),
        ('texto', wagtail_blocks.RichTextBlock(label="Texto")),
        ('html', wagtail_blocks.RawHTMLBlock(label="HTML Customizado")),
    ], blank=True, use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]
    
    class Meta:
        verbose_name = "Página Dashboard"
        verbose_name_plural = "Páginas Dashboard"
```

## Template (dashboard_page.html)
```django
{% extends "base.html" %}
{% load static wagtailcore_tags %}

{% block title %}{{ page.title }} | Gestão de Estoque{% endblock %}

{% block body_class %}dashboard-page{% endblock %}

{% comment %}
❌ NÃO incluir breadcrumbs aqui - já está no base.html
❌ NÃO forçar título aqui - deixar cliente escolher via StreamField
{% endcomment %}

{% block content %}

{# Renderizar blocos customizáveis do Wagtail #}
{% for block in page.body %}
    <div class="block-{{ block.block_type }}">
        {% include_block block %}
    </div>
{% endfor %}

{# Conteúdo fixo (se necessário) #}
<div class="container-fluid">
    <div class="row g-4">
        
        <!-- Produtos Mais Vendidos -->
        <div class="col-lg-6">
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-white border-bottom">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-graph-up me-2"></i>
                        Produtos Mais Vendidos
                    </h5>
                </div>
                <div class="card-body">
                    {% if top_products %}
                        {# Lista de produtos #}
                    {% else %}
                        <p class="text-muted text-center py-4">Nenhum dado disponível</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
    </div>
</div>

{% endblock %}

{% block extra_js %}
<script src="{% static 'js/dashboard/dashboard.js' %}"></script>
{% endblock %}
```

## Blocos Wagtail (blocks/blocks.py)
```python
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

class TituloBlock(blocks.StructBlock):
    """
    Bloco de título customizável.
    Cliente escolhe texto, ícone, cor de fundo.
    """
    titulo = blocks.CharBlock(label="Título", max_length=255)
    subtitulo = blocks.CharBlock(label="Subtítulo", max_length=255, required=False)
    icone = blocks.CharBlock(
        label="Ícone Bootstrap",
        max_length=50,
        required=False,
        help_text="Ex: speedometer2, box-seam, graph-up"
    )
    cor_fundo = blocks.ChoiceBlock(
        label="Cor de Fundo",
        choices=[
            ('', 'Nenhuma'),
            ('bg-primary', 'Primária'),
            ('bg-secondary', 'Secundária'),
            ('bg-light', 'Clara'),
            ('bg-dark', 'Escura'),
        ],
        required=False
    )
    centralizado = blocks.BooleanBlock(label="Centralizado", required=False)
    
    class Meta:
        template = 'blocks/titulo.html'
        icon = 'title'
        label = 'Título'

class CardBlock(blocks.StructBlock):
    """
    Card de métrica customizável.
    """
    titulo = blocks.CharBlock(label="Título", max_length=100)
    valor = blocks.CharBlock(label="Valor", max_length=50)
    icone = blocks.CharBlock(label="Ícone", max_length=50)
    cor = blocks.ChoiceBlock(
        label="Cor",
        choices=[
            ('primary', 'Azul'),
            ('success', 'Verde'),
            ('warning', 'Amarelo'),
            ('danger', 'Vermelho'),
        ]
    )
    
    class Meta:
        template = 'blocks/card_metrica.html'
        icon = 'doc-full'
        label = 'Card de Métrica'
```

## Template do Bloco (blocks/titulo.html)
```django
{% load wagtailcore_tags %}

<div class="page-titulo {{ value.cor_fundo }} {% if value.centralizado %}text-center{% endif %} py-4">
    <div class="container-fluid">
        <h1 class="page-titulo__title h2 mb-2">
            {% if value.icone %}
                <i class="bi bi-{{ value.icone }} me-2"></i>
            {% endif %}
            {{ value.titulo }}
        </h1>
        {% if value.subtitulo %}
            <p class="page-titulo__subtitle text-muted mb-0">{{ value.subtitulo }}</p>
        {% endif %}
    </div>
</div>
```

## Uso no Wagtail Admin

1. Cliente acessa **/admin/pages/**
2. Cria nova "Página Dashboard"
3. Adiciona blocos arrastando da barra lateral:
   - **Título**: "Dashboard Principal" com ícone "speedometer2"
   - **Card Métrica**: "Total de Produtos" com valor dinâmico
   - **Banner**: Imagem promocional
   - **Texto Rico**: Instruções para usuários
4. Reordena blocos arrastando
5. Publica página

## Resultado

✅ Cliente customiza conteúdo sem alterar código
✅ Layout responsivo e acessível
✅ Cada página pode ter estrutura diferente
✅ Blocos reutilizáveis entre páginas
✅ base.html fornece estrutura consistente (header, menu, footer)
✅ Breadcrumbs automáticos
✅ Título opcional (via bloco TituloBlock ou page_header)
