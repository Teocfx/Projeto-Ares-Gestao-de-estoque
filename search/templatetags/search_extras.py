from django import template

register = template.Library()

@register.filter
def result_type(result):
    """Retorna o tipo do resultado de busca."""
    # Models do sistema de gestão de estoque
    class_name = result.__class__.__name__
    
    if class_name == "Product":
        return "Produto"
    elif class_name == "InventoryMovement":
        return "Movimentação"
    elif class_name == "Category":
        return "Categoria"
    # Para objetos Page do Wagtail
    elif hasattr(result, "content_type") and hasattr(result.content_type, "model"):
        tipo = result.content_type.model
        if tipo.lower() == "document":
            return "Documento"
        if tipo.lower() == "image":
            return "Imagem"
        return tipo.replace('_', ' ').title()
    # Caso seja string ou outro tipo
    elif isinstance(result, str):
        return result.replace('_', ' ').title()
    return ""