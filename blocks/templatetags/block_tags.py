"""
Template tags customizadas para componentes reutilizáveis do sistema.

Usado por: table.html, card.html e outros componentes
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Obtém um valor de um dicionário usando uma chave.
    
    Uso no template:
    {{ row|get_item:header.field }}
    
    Exemplo:
    Se row = {'nome': 'Produto A', 'estoque': 100}
    E header.field = 'nome'
    Retorna: 'Produto A'
    
    Args:
        dictionary: Dicionário ou objeto com atributos
        key: Chave a ser acessada
        
    Returns:
        Valor encontrado ou None
    """
    if dictionary is None:
        return None
    
    # Se for um dicionário
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    
    # Se for um objeto (model instance, etc.)
    try:
        return getattr(dictionary, key)
    except (AttributeError, TypeError):
        return None


@register.filter
def status_badge_class(status):
    """
    Retorna a classe CSS Bootstrap apropriada para um status.
    
    Uso no template:
    <span class="badge {{ status|status_badge_class }}">{{ status }}</span>
    
    Args:
        status: String representando o status
        
    Returns:
        String com classe CSS Bootstrap
    """
    status_map = {
        'CRITICO': 'bg-danger',
        'CRÍTICO': 'bg-danger',
        'critico': 'bg-danger',
        'crítico': 'bg-danger',
        'BAIXO': 'bg-warning',
        'baixo': 'bg-warning',
        'OK': 'bg-success',
        'ok': 'bg-success',
        'ATIVO': 'bg-success',
        'ativo': 'bg-success',
        'INATIVO': 'bg-secondary',
        'inativo': 'bg-secondary',
        'PENDENTE': 'bg-warning',
        'pendente': 'bg-warning',
        'APROVADO': 'bg-success',
        'aprovado': 'bg-success',
        'REJEITADO': 'bg-danger',
        'rejeitado': 'bg-danger',
    }
    
    return status_map.get(str(status), 'bg-primary')


@register.filter
def multiply(value, arg):
    """
    Multiplica um valor por um argumento.
    
    Uso no template:
    {{ preco|multiply:quantidade }}
    
    Args:
        value: Valor numérico
        arg: Multiplicador
        
    Returns:
        Resultado da multiplicação ou None se inválido
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return None
