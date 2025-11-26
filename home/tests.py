"""
Testes para o app home (Wagtail CMS).
Testa models, páginas e blocos do Wagtail.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from wagtail.models import Site, Page

from home.models import HomePage, BannerBlock, DestaqueBlock, NoticiaBlock


User = get_user_model()


class HomePageModelTestCase(TestCase):
    """Testes para o modelo HomePage."""
    
    def setUp(self):
        """Configuração inicial."""
        # Obter a página raiz
        self.root_page = Page.objects.get(id=1)
        
        # Criar HomePage
        self.home_page = HomePage(
            title='Home Page Teste',
            slug='home-teste',
            show_in_menus=True,
            hero_title='Título Hero Teste'
        )
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
    
    def test_homepage_creation(self):
        """Testa criação de HomePage."""
        self.assertIsInstance(self.home_page, HomePage)
        self.assertEqual(self.home_page.title, 'Home Page Teste')
        self.assertTrue(self.home_page.live)
    
    def test_homepage_has_required_fields(self):
        """Testa que HomePage tem os campos necessários."""
        self.assertTrue(hasattr(self.home_page, 'title'))
        self.assertTrue(hasattr(self.home_page, 'show_in_menus'))
    
    def test_homepage_slug_is_unique(self):
        """Testa que o slug da HomePage é único."""
        # Tentar criar outra HomePage com mesmo slug deve falhar
        with self.assertRaises(Exception):
            duplicate_page = HomePage(
                title='Outra Home',
                slug='home-teste',
                hero_title='Título Duplicado'
            )
            self.root_page.add_child(instance=duplicate_page)
    
    def test_homepage_can_be_published(self):
        """Testa que HomePage pode ser publicada."""
        self.assertTrue(self.home_page.live)
        # Página foi salva e está ativa
        self.assertTrue(self.home_page.id is not None)
    
    def test_homepage_appears_in_site(self):
        """Testa que HomePage aparece no site."""
        # Configurar HomePage como página raiz do site
        site = Site.objects.get(is_default_site=True)
        site.root_page = self.home_page
        site.save()
        
        self.assertEqual(site.root_page, self.home_page)


class HomePageViewTestCase(TestCase):
    """Testes para visualização da HomePage."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        
        # Obter a página raiz
        self.root_page = Page.objects.get(id=1)
        
        # Criar HomePage
        self.home_page = HomePage(
            title='Home Pública',
            slug='home-pub',
            show_in_menus=True,
            hero_title='Título Hero Pública'
        )
        self.root_page.add_child(instance=self.home_page)
        self.home_page.save_revision().publish()
        
        # Configurar como página raiz do site
        site = Site.objects.get(is_default_site=True)
        site.root_page = self.home_page
        site.save()
    
    def test_homepage_exists_in_database(self):
        """Testa que a HomePage existe no banco de dados."""
        # Verificar que a página foi criada e está ativa
        self.assertTrue(self.home_page.id is not None)
        self.assertTrue(self.home_page.live)
    
    def test_homepage_has_correct_url(self):
        """Testa que a HomePage tem a URL correta."""
        # Verificar que a página tem um slug válido
        self.assertEqual(self.home_page.slug, 'home-pub')
        self.assertTrue(len(self.home_page.url) > 0)
    
    def test_homepage_displays_hero_title(self):
        """Testa que a HomePage tem hero_title configurado."""
        self.assertEqual(self.home_page.hero_title, 'Título Hero Pública')
    
    def test_homepage_is_configured_as_root(self):
        """Testa que a HomePage foi configurada como raiz do site."""
        # Garantir que foi configurada
        site = Site.objects.get(is_default_site=True)
        self.assertEqual(site.root_page.id, self.home_page.id)


class BannerBlockTestCase(TestCase):
    """Testes para o bloco BannerBlock."""
    
    def test_banner_block_structure(self):
        """Testa a estrutura do BannerBlock."""
        block = BannerBlock()
        
        # Verificar campos
        self.assertIn('title', block.child_blocks)
        self.assertIn('subtitle', block.child_blocks)
        self.assertIn('image', block.child_blocks)
        self.assertIn('button_text', block.child_blocks)
        self.assertIn('button_link', block.child_blocks)
    
    def test_banner_block_meta(self):
        """Testa metadados do BannerBlock."""
        block = BannerBlock()
        self.assertEqual(block.meta.template, 'home/blocks/banner_block.html')
        self.assertEqual(block.meta.icon, 'image')
        self.assertEqual(block.meta.label, 'Banner')
    
    def test_banner_block_required_fields(self):
        """Testa campos obrigatórios do BannerBlock."""
        block = BannerBlock()
        
        # Title e image são obrigatórios
        self.assertFalse(block.child_blocks['subtitle'].required)
        self.assertFalse(block.child_blocks['button_text'].required)
        self.assertFalse(block.child_blocks['button_link'].required)


class DestaqueBlockTestCase(TestCase):
    """Testes para o bloco DestaqueBlock."""
    
    def test_destaque_block_structure(self):
        """Testa a estrutura do DestaqueBlock."""
        block = DestaqueBlock()
        
        # Verificar campos
        self.assertIn('title', block.child_blocks)
        self.assertIn('description', block.child_blocks)
        self.assertIn('image', block.child_blocks)
        self.assertIn('link', block.child_blocks)
        self.assertIn('icon', block.child_blocks)
    
    def test_destaque_block_meta(self):
        """Testa metadados do DestaqueBlock."""
        block = DestaqueBlock()
        self.assertEqual(block.meta.template, 'home/blocks/destaque_block.html')
        self.assertEqual(block.meta.icon, 'pick')
        self.assertEqual(block.meta.label, 'Destaque')
    
    def test_destaque_block_icon_field(self):
        """Testa campo de ícone do DestaqueBlock."""
        block = DestaqueBlock()
        icon_field = block.child_blocks['icon']
        
        # Verificar que o campo de ícone existe e é CharBlock
        self.assertIsNotNone(icon_field)
        self.assertEqual(type(icon_field).__name__, 'CharBlock')


class NoticiaBlockTestCase(TestCase):
    """Testes para o bloco NoticiaBlock."""
    
    def test_noticia_block_structure(self):
        """Testa a estrutura do NoticiaBlock."""
        block = NoticiaBlock()
        
        # Verificar campos
        self.assertIn('title', block.child_blocks)
        self.assertIn('summary', block.child_blocks)
    
    def test_noticia_block_meta(self):
        """Testa metadados do NoticiaBlock."""
        block = NoticiaBlock()
        self.assertEqual(block.meta.template, 'home/blocks/noticia_block.html')


class WagtailIntegrationTestCase(TestCase):
    """Testes de integração com Wagtail."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
    
    def test_wagtail_admin_accessible(self):
        """Testa que o admin do Wagtail está acessível."""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_editable_in_admin(self):
        """Testa que HomePage é editável no admin."""
        # Obter a página raiz
        root_page = Page.objects.get(id=1)
        
        # Criar HomePage
        home_page = HomePage(
            title='Home Editável',
            slug='home-edit',
            hero_title='Título Hero Editável'
        )
        root_page.add_child(instance=home_page)
        
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/admin/pages/{home_page.id}/edit/')
        self.assertEqual(response.status_code, 200)
    
    def test_homepage_can_be_deleted(self):
        """Testa que HomePage pode ser deletada."""
        # Obter a página raiz
        root_page = Page.objects.get(id=1)
        
        # Criar HomePage
        home_page = HomePage(
            title='Home Deletável',
            slug='home-delete',
            hero_title='Título Hero Deletável'
        )
        root_page.add_child(instance=home_page)
        
        page_id = home_page.id
        home_page.delete()
        
        # Verificar que foi deletada
        self.assertFalse(Page.objects.filter(id=page_id).exists())
