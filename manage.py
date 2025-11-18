#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.
Sistema de Gestão de Estoque ARES.
"""

import os
import sys

# Adiciona o diretório raiz ao path do Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    # Se dotenv não estiver disponível, tenta carregar .env manualmente
    from pathlib import Path
    env_file = Path(__file__).resolve().parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    """Run administrative tasks."""
    
    # Define o módulo de settings baseado no ambiente
    ambiente = os.environ.get('AMBIENTE', 'dev')
    if ambiente == 'production':
        default_settings = "siteares.settings.production"
    elif ambiente in ('test', 'testing'):
        default_settings = "siteares.settings.testing"
    else:
        default_settings = "siteares.settings.dev"
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
