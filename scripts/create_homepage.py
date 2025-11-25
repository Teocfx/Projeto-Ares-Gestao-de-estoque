#!/usr/bin/env python
"""
Script para criar a HomePage inicial com conteúdo de exemplo.
Execute: python manage.py runscript create_homepage
Ou: python scripts/create_homepage.py
"""

import os
import sys
import django

# Setup Django
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteares.settings.dev")
    django.setup()

from wagtail.models import Site
from home.models import HomePage


def run():
    """Cria a HomePage inicial se não existir."""
    
    # Verificar se já existe uma HomePage
    if HomePage.objects.exists():
        print("❌ HomePage já existe. Abortando...")
        homepage = HomePage.objects.first()
        print(f"   URL: http://127.0.0.1:8000{homepage.url}")
        return
    
    print("🏗️  Criando HomePage inicial...")
    
    # Obter o site raiz
    try:
        site = Site.objects.get(is_default_site=True)
        root_page = site.root_page
    except Site.DoesNotExist:
        print("❌ Site padrão não encontrado!")
        return
    
    # Criar a HomePage
    homepage = HomePage(
        title="Sistema ARES - Gestão de Estoque",
        slug="home",
        hero_title="Sistema ARES",
        hero_subtitle="Sistema de Gestão de Estoque Inteligente e Eficiente",
        destaques_title="Principais Funcionalidades",
        noticias_title="Últimas Atualizações",
        footer_text="<p>Sistema ARES © 2025 - Todos os direitos reservados</p>",
        show_in_menus=True,
    )
    
    # Adicionar como filho da página raiz
    root_page.add_child(instance=homepage)
    
    # Publicar a página
    homepage.save_revision().publish()
    
    # Configurar como página inicial do site
    site.root_page = homepage
    site.save()
    
    print("✅ HomePage criada com sucesso!")
    print(f"   Título: {homepage.title}")
    print(f"   URL: http://127.0.0.1:8000{homepage.url}")
    print(f"   Status: {'Publicada' if homepage.live else 'Rascunho'}")
    print()
    print("📝 Próximos passos:")
    print("   1. Acesse o Wagtail Admin: http://127.0.0.1:8000/admin/")
    print("   2. Edite a HomePage para adicionar banners, destaques e notícias")
    print("   3. Faça upload de imagens para o hero e banners")
    print("   4. Personalize o conteúdo através dos StreamFields")
    print()
    print("💡 Dica: Use os StreamFields para adicionar:")
    print("   - Banners no carrossel principal")
    print("   - Destaques com ícones e imagens")
    print("   - Notícias/Blog posts")
    print("   - Call-to-Actions (CTAs)")
    print("   - Blocos de texto com imagens")


if __name__ == "__main__":
    run()
