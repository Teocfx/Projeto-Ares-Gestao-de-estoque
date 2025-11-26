#!/usr/bin/env python3
"""
Script para verificar se todas as dependências necessárias estão instaladas.
Execute: python check-dependencies.py
"""

import sys

# Lista de módulos críticos que precisam estar instalados
REQUIRED_MODULES = [
    ('django', 'Django'),
    ('wagtail', 'Wagtail'),
    ('rest_framework', 'djangorestframework'),
    ('decouple', 'python-decouple'),
    ('PIL', 'Pillow'),
    ('corsheaders', 'django-cors-headers'),
    ('drf_yasg', 'drf-yasg'),
    ('rest_framework_simplejwt', 'djangorestframework-simplejwt'),
    ('webpack_loader', 'django-webpack-loader'),
    ('allauth', 'django-allauth'),
]

def check_dependencies():
    """Verifica se todas as dependências estão instaladas."""
    print("🔍 Verificando dependências...\n")
    
    missing = []
    installed = []
    
    for module_name, package_name in REQUIRED_MODULES:
        try:
            __import__(module_name)
            installed.append(f"✅ {package_name}")
        except ImportError:
            missing.append(f"❌ {package_name} (pip install {package_name})")
    
    # Exibir resultados
    if installed:
        print("📦 Pacotes instalados:")
        for pkg in installed:
            print(f"  {pkg}")
    
    if missing:
        print("\n❌ Pacotes faltando:")
        for pkg in missing:
            print(f"  {pkg}")
        print("\n💡 Para instalar todas as dependências:")
        print("   pip install -r requirements/local.txt")
        sys.exit(1)
    else:
        print("\n✅ Todas as dependências necessárias estão instaladas!")
        print("🚀 Você pode executar: python manage.py runserver")
        sys.exit(0)

if __name__ == "__main__":
    check_dependencies()
