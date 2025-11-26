"""
Models para páginas públicas do site com Wagtail CMS.
"""
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail import blocks


# StreamField Blocks personalizados

class BannerBlock(blocks.StructBlock):
    """Bloco de banner/slide para carrossel."""
    title = blocks.CharBlock(label="Título", max_length=100)
    subtitle = blocks.CharBlock(label="Subtítulo", max_length=200, required=False)
    image = ImageChooserBlock(label="Imagem")
    button_text = blocks.CharBlock(label="Texto do Botão", max_length=50, required=False)
    button_link = blocks.URLBlock(label="Link do Botão", required=False)
    
    class Meta:
        template = 'home/blocks/banner_block.html'
        icon = 'image'
        label = 'Banner'


class DestaqueBlock(blocks.StructBlock):
    """Bloco de destaque com imagem e texto."""
    title = blocks.CharBlock(label="Título", max_length=100)
    description = blocks.TextBlock(label="Descrição", max_length=300)
    image = ImageChooserBlock(label="Imagem")
    link = blocks.URLBlock(label="Link", required=False)
    icon = blocks.CharBlock(
        label="Ícone Bootstrap Icons",
        max_length=50,
        required=False,
        help_text="Ex: bi-box, bi-truck, bi-star"
    )
    
    class Meta:
        template = 'home/blocks/destaque_block.html'
        icon = 'pick'
        label = 'Destaque'


class NoticiaBlock(blocks.StructBlock):
    """Bloco de notícia/post."""
    title = blocks.CharBlock(label="Título", max_length=150)
    summary = blocks.TextBlock(label="Resumo", max_length=300)
    image = ImageChooserBlock(label="Imagem", required=False)
    date = blocks.DateBlock(label="Data")
    author = blocks.CharBlock(label="Autor", max_length=100, required=False)
    link = blocks.URLBlock(label="Link completo", required=False)
    
    class Meta:
        template = 'home/blocks/noticia_block.html'
        icon = 'doc-full'
        label = 'Notícia'


class CallToActionBlock(blocks.StructBlock):
    """Bloco de call-to-action."""
    title = blocks.CharBlock(label="Título", max_length=100)
    text = blocks.RichTextBlock(label="Texto")
    button_text = blocks.CharBlock(label="Texto do Botão", max_length=50)
    button_link = blocks.URLBlock(label="Link do Botão")
    background_color = blocks.ChoiceBlock(
        label="Cor de Fundo",
        choices=[
            ('primary', 'Azul Primário'),
            ('secondary', 'Cinza'),
            ('success', 'Verde'),
            ('info', 'Azul Claro'),
            ('warning', 'Amarelo'),
            ('danger', 'Vermelho'),
        ],
        default='primary'
    )
    
    class Meta:
        template = 'home/blocks/cta_block.html'
        icon = 'warning'
        label = 'Call to Action'


class TextoComImagemBlock(blocks.StructBlock):
    """Bloco de texto com imagem lateral."""
    title = blocks.CharBlock(label="Título", max_length=100)
    text = blocks.RichTextBlock(label="Texto")
    image = ImageChooserBlock(label="Imagem")
    image_position = blocks.ChoiceBlock(
        label="Posição da Imagem",
        choices=[
            ('left', 'Esquerda'),
            ('right', 'Direita'),
        ],
        default='right'
    )
    
    class Meta:
        template = 'home/blocks/texto_imagem_block.html'
        icon = 'doc-full-inverse'
        label = 'Texto com Imagem'


# Página inicial

class HomePage(Page):
    """
    Página inicial do site público.
    Configurável via admin do Wagtail com StreamFields.
    """
    max_count = 1  # Apenas uma homepage
    
    # Cabeçalho
    hero_title = models.CharField(
        "Título Principal",
        max_length=200,
        help_text="Título principal exibido no topo da página"
    )
    
    hero_subtitle = models.CharField(
        "Subtítulo",
        max_length=300,
        blank=True,
        help_text="Subtítulo opcional"
    )
    
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Imagem de Fundo"
    )
    
    # Banner rotativo
    banners = StreamField([
        ('banner', BannerBlock()),
    ], blank=True, null=True, use_json_field=True, verbose_name="Banners")
    
    # Seção de destaques
    destaques_title = models.CharField(
        "Título da Seção Destaques",
        max_length=100,
        default="Nossos Diferenciais",
        blank=True
    )
    
    destaques = StreamField([
        ('destaque', DestaqueBlock()),
    ], blank=True, null=True, use_json_field=True, verbose_name="Destaques")
    
    # Conteúdo flexível
    body = StreamField([
        ('texto_imagem', TextoComImagemBlock()),
        ('call_to_action', CallToActionBlock()),
        ('destaque', DestaqueBlock()),
    ], blank=True, null=True, use_json_field=True, verbose_name="Conteúdo")
    
    # Seção de notícias
    noticias_title = models.CharField(
        "Título da Seção Notícias",
        max_length=100,
        default="Últimas Notícias",
        blank=True
    )
    
    noticias = StreamField([
        ('noticia', NoticiaBlock()),
    ], blank=True, null=True, use_json_field=True, verbose_name="Notícias")
    
    # Rodapé customizado
    footer_text = RichTextField(
        "Texto do Rodapé",
        blank=True,
        help_text="Texto adicional para o rodapé"
    )
    
    # Painéis do admin
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('hero_title'),
            FieldPanel('hero_subtitle'),
            FieldPanel('hero_image'),
        ], heading="Cabeçalho Principal"),
        
        MultiFieldPanel([
            FieldPanel('banners'),
        ], heading="Carrossel de Banners"),
        
        MultiFieldPanel([
            FieldPanel('destaques_title'),
            FieldPanel('destaques'),
        ], heading="Seção de Destaques"),
        
        FieldPanel('body'),
        
        MultiFieldPanel([
            FieldPanel('noticias_title'),
            FieldPanel('noticias'),
        ], heading="Seção de Notícias"),
        
        MultiFieldPanel([
            FieldPanel('footer_text'),
        ], heading="Rodapé"),
    ]
    
    class Meta:
        verbose_name = "Página Inicial"
        verbose_name_plural = "Páginas Iniciais"


# Página interna genérica

class InternalPage(Page):
    """
    Página interna genérica com conteúdo flexível.
    """
    intro = models.CharField(
        "Introdução",
        max_length=300,
        blank=True
    )
    
    body = StreamField([
        ('texto_imagem', TextoComImagemBlock()),
        ('call_to_action', CallToActionBlock()),
        ('destaque', DestaqueBlock()),
        ('heading', blocks.CharBlock(label="Título", classname="title")),
        ('paragraph', blocks.RichTextBlock(label="Parágrafo")),
        ('image', ImageChooserBlock(label="Imagem")),
    ], blank=True, null=True, use_json_field=True, verbose_name="Conteúdo")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
    
    class Meta:
        verbose_name = "Página Interna"
        verbose_name_plural = "Páginas Internas"
