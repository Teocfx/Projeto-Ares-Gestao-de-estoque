# -*- coding: utf-8 -*-

default_app_config = 'siteares.apps.SitearesConfig'

__version__ = '1.0.0'
__version_info__ = (1, 0, 0)
__api_version__ = 'v1'

def get_version():
    """Retorna versão completa do sistema."""
    return __version__