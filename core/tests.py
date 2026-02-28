"""
Testes para o módulo core.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from wagtail.documents.models import Document
from wagtail.documents.tests.utils import get_test_document_file

from produtos.models import Category, Unit

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
        response = self.client.get(reverse('core:teste_componentes'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


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
        url = reverse('core:document_serve_inline', kwargs={
            'document_id': self.document.id,
            'document_filename': self.document.filename
        })
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class CoreUtilsTests(TestCase):
    """Testes para utilitários do core."""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Test Category',
            is_active=True
        )
        self.unit = Unit.objects.create(name='UN', description='Unidade')


@override_settings(
    STORAGES={
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
    }
)
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

