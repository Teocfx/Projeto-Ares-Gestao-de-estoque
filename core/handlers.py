"""
Handlers personalizados para erros HTTP.
"""

from django.shortcuts import redirect
from django.contrib import messages


def permission_denied_handler(request, exception=None):
    """
    Handler personalizado para erro 403 - Permissão Negada.
    Redireciona usuários sem permissão para o dashboard com mensagem.
    """
    messages.error(
        request,
        'Você não tem permissão para acessar esta página. '
        'Entre em contato com o administrador se precisar de acesso.'
    )
    return redirect('dashboard:index')
