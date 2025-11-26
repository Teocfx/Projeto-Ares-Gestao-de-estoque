"""
Testes para o módulo core.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from wagtail.documents.models import Document
from wagtail.documents.tests.utils import get_test_document_file

from .models import TimeStampedModel, UserTrackingModel, SiteConfiguration
from produtos.models import Product, Category, Unit
from decimal import Decimal

User = get_user_model()


class TimeStampedModelTests(TestCase):
    """Testes para o modelo abstrato TimeStampedModel."""
    
    def test_timestamps_auto_created(self):
        """Testa se os timestamps são criados automaticamente."""
        category = Category.objects.create(
            name='Test Category',
            is_active=True
        )
        
        self.assertIsNotNone(category.created_at)
        self.assertIsNotNone(category.updated_at)
    
    def test_updated_at_changes_on_save(self):
        """Testa se updated_at é atualizado ao salvar."""
        category = Category.objects.create(
            name='Test Category',
            is_active=True
        )
        
        original_updated = category.updated_at
        
        # Pequeno delay e atualização
        import time
        time.sleep(0.1)
        
        category.name = 'Updated Category'
        category.save()
        
        self.assertGreater(category.updated_at, original_updated)


class SiteConfigurationTests(TestCase):
    """Testes para as configurações do site."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
    
    def test_site_configuration_creation(self):
        """Testa criação de configuração do site."""
        # A configuração é criada automaticamente via Wagtail
        # Podemos acessá-la através do registro
        from wagtail.models import Site
        
        site = Site.objects.get(is_default_site=True)
        self.assertIsNotNone(site)
        self.assertTrue(site.is_default_site)


class TesteComponentesViewTests(TestCase):
    """Testes para a view de teste de componentes."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_view_requires_login(self):
        """Testa se a view requer autenticação."""
        response = self.client.get(reverse('core:teste-componentes'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_view_loads_when_authenticated(self):
        """Testa se a view carrega quando autenticado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:teste-componentes'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'teste_componentes.html')
    
    def test_view_context_has_breadcrumbs_disabled(self):
        """Testa se breadcrumbs estão desabilitados."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:teste-componentes'))
        
        self.assertFalse(response.context['show_breadcrumbs'])


class DocumentServeViewTests(TestCase):
    """Testes para a view de servir documentos."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Criar documento de teste
        self.document = Document.objects.create(
            title='Test Document',
            file=get_test_document_file()
        )
    
    def test_serve_existing_document(self):
        """Testa servir um documento existente."""
        url = reverse('core:document_serve', kwargs={
            'document_id': self.document.id,
            'document_filename': self.document.filename
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_serve_nonexistent_document(self):
        """Testa servir um documento inexistente."""
        url = reverse('core:document_serve', kwargs={
            'document_id': 99999,
            'document_filename': 'nonexistent.pdf'
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CoreUtilsTests(TestCase):
    """Testes para utilitários do core."""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            is_active=True
        )
        self.unit = Unit.objects.create(
            name='Unidade',
            abbreviation='un',
            is_active=True
        )
    
    def test_model_ordering(self):
        """Testa ordenação padrão por created_at."""
        product1 = Product.objects.create(
            name='Produto 1',
            sku='SKU001',
            category=self.category,
            unit=self.unit,
            current_stock=10,
            min_stock=5,
            price=Decimal('10.00'),
            is_active=True
        )
        
        import time
        time.sleep(0.1)
        
        product2 = Product.objects.create(
            name='Produto 2',
            sku='SKU002',
            category=self.category,
            unit=self.unit,
            current_stock=20,
            min_stock=5,
            price=Decimal('20.00'),
            is_active=True
        )
        
        # Por padrão, o mais recente deve vir primeiro
        products = Product.objects.all()
        self.assertEqual(products.first(), product2)


class PermissionTests(TestCase):
    """Testes para verificação de permissões."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unauthorized_access_redirects(self):
        """Testa se acesso não autorizado redireciona para login."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_authorized_access_succeeds(self):
        """Testa se acesso autorizado funciona."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
