"""
Configuração do app autenticacao_2fa.
"""
from django.apps import AppConfig


class Autenticacao2FaConfig(AppConfig):
    """Configuração do app de autenticação de dois fatores."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'autenticacao_2fa'
    verbose_name = 'Autenticação de Dois Fatores (2FA)'
