"""
Management command para criar página Home da Loja automaticamente.
Executado após migrate ou manualmente com: python manage.py setup_loja_home
"""
from django.core.management.base import BaseCommand
from wagtail.models import Site, Page
from home.models import HomePage


class Command(BaseCommand):
    help = 'Cria página Home da Loja automaticamente se não existir'

    def handle(self, *args, **options):
        self.stdout.write('Verificando estrutura de páginas Wagtail...')
        
        try:
            # Buscar a página root
            root = Page.objects.get(depth=1)
            self.stdout.write(f'✓ Página root encontrada: {root.title}')
            
            # Verificar se já existe uma HomePage
            if HomePage.objects.exists():
                home_page = HomePage.objects.first()
                self.stdout.write(f'✓ Página Home já existe: {home_page.title}')
            else:
                # Criar HomePage
                home_page = HomePage(
                    title='Loja ARES',
                    slug='home',
                    live=True,
                    show_in_menus=True,
                )
                root.add_child(instance=home_page)
                self.stdout.write(self.style.SUCCESS('✓ Página Home criada: Loja ARES'))
            
            # Configurar ou atualizar Site
            site, created = Site.objects.get_or_create(
                hostname='localhost',
                defaults={
                    'root_page': home_page,
                    'is_default_site': True,
                    'site_name': 'ARES - Sistema de Gestão de Estoque',
                }
            )
            
            if not created and site.root_page != home_page:
                site.root_page = home_page
                site.save()
                self.stdout.write(self.style.SUCCESS('✓ Site atualizado para usar HomePage'))
            elif created:
                self.stdout.write(self.style.SUCCESS('✓ Site criado: ARES'))
            else:
                self.stdout.write('✓ Site já configurado corretamente')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Configuração concluída!'))
            self.stdout.write('   - Loja: http://localhost:8000/loja/')
            self.stdout.write('   - Dashboard: http://localhost:8000/dashboard/')
            
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR('✗ Erro: Página root não encontrada'))
            self.stdout.write('  Execute: python manage.py migrate wagtailcore')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro: {str(e)}'))
