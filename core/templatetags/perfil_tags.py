"""
Template tags para controle de acesso baseado em perfis.
"""
from django import template
from core.models import PerfilAcesso, PerfilUsuario

register = template.Library()


@register.filter
def tem_perfil(user, perfil_nome):
    """
    Verifica se o usuário tem um perfil específico.
    
    Usage:
        {% if request.user|tem_perfil:'REPR_LEGAL' %}
        {% if request.user|tem_perfil:'REPR_DELEGADO' %}
        {% if request.user|tem_perfil:'OPERADOR' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        perfil = user.perfil
        if not perfil.ativo:
            return False
        return perfil.perfil == perfil_nome
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.filter
def tem_permissao(user, permissao):
    """
    Verifica se o usuário tem uma permissão específica.
    
    Usage:
        {% if request.user|tem_permissao:'editar_produtos' %}
        {% if request.user|tem_permissao:'gerar_relatorios' %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        return user.perfil.tem_permissao(permissao)
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.filter
def is_representante_legal(user):
    """
    Verifica se o usuário é Representante Legal.
    
    Usage:
        {% if request.user|is_representante_legal %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        return user.perfil.is_representante_legal()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.filter
def is_representante_delegado(user):
    """
    Verifica se o usuário é Representante Delegado.
    
    Usage:
        {% if request.user|is_representante_delegado %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        return user.perfil.is_representante_delegado()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.filter
def is_representante(user):
    """
    Verifica se o usuário é Representante (Legal ou Delegado).
    
    Usage:
        {% if request.user|is_representante %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        perfil = user.perfil
        return perfil.is_representante_legal() or perfil.is_representante_delegado()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.filter
def is_operador(user):
    """
    Verifica se o usuário é Operador.
    
    Usage:
        {% if request.user|is_operador %}
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        return user.perfil.is_operador()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


@register.simple_tag
def get_perfil_display(user):
    """
    Retorna o nome do perfil do usuário.
    
    Usage:
        {% get_perfil_display request.user %}
    """
    if not user or not user.is_authenticated:
        return "Visitante"
    
    try:
        return user.perfil.get_perfil_display()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return "Sem perfil"


@register.simple_tag
def get_perfil_badge_class(user):
    """
    Retorna a classe CSS do badge do perfil.
    
    Usage:
        <span class="badge {% get_perfil_badge_class request.user %}">
            {% get_perfil_display request.user %}
        </span>
    """
    if not user or not user.is_authenticated:
        return "bg-secondary"
    
    try:
        perfil = user.perfil.perfil
        badges = {
            PerfilAcesso.REPRESENTANTE_LEGAL: "bg-danger",
            PerfilAcesso.REPRESENTANTE_DELEGADO: "bg-warning",
            PerfilAcesso.OPERADOR: "bg-info",
        }
        return badges.get(perfil, "bg-secondary")
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return "bg-secondary"


@register.inclusion_tag('core/components/perfil_badge.html')
def perfil_badge(user):
    """
    Renderiza um badge com o perfil do usuário.
    
    Usage:
        {% load perfil_tags %}
        {% perfil_badge request.user %}
    """
    if not user or not user.is_authenticated:
        return {
            'perfil_display': 'Visitante',
            'badge_class': 'bg-secondary',
            'has_perfil': False
        }
    
    try:
        perfil = user.perfil
        badges = {
            PerfilAcesso.REPRESENTANTE_LEGAL: "bg-danger",
            PerfilAcesso.REPRESENTANTE_DELEGADO: "bg-warning",
            PerfilAcesso.OPERADOR: "bg-info",
        }
        return {
            'perfil_display': perfil.get_perfil_display(),
            'badge_class': badges.get(perfil.perfil, "bg-secondary"),
            'has_perfil': True,
            'ativo': perfil.ativo
        }
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return {
            'perfil_display': 'Sem perfil',
            'badge_class': 'bg-secondary',
            'has_perfil': False
        }


@register.filter
def pprint(value):
    """
    Formata JSON de forma legível (pretty print).
    
    Usage:
        {{ my_dict|pprint }}
    """
    import json
    try:
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)
