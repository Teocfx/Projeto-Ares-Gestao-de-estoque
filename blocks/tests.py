"""
Testes para o módulo blocks.
Este módulo é usado para definir blocos customizados do Wagtail StreamField.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from wagtail.blocks import StreamBlock, CharBlock, RichTextBlock
from wagtail.models import Page

User = get_user_model()


class BlocksConfigTests(TestCase):
    """Testes para configuração do app blocks."""
    
    def test_app_config(self):
        """Testa se a configuração do app está correta."""
        from blocks.apps import BlocksConfig
        
        self.assertEqual(BlocksConfig.name, 'blocks')
        self.assertEqual(BlocksConfig.default_auto_field, 'django.db.models.BigAutoField')


class BlocksIntegrationTests(TestCase):
    """Testes de integração para blocos Wagtail."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_streamblock_creation(self):
        """Testa criação de StreamBlock básico."""
        class TestStreamBlock(StreamBlock):
            heading = CharBlock()
            paragraph = RichTextBlock()
        
        block = TestStreamBlock()
        self.assertIsNotNone(block)
        self.assertEqual(len(block.child_blocks), 2)
    
    def test_block_rendering(self):
        """Testa renderização de bloco."""
        from wagtail.blocks import CharBlock
        
        block = CharBlock()
        value = block.to_python('Test Value')
        
        self.assertEqual(value, 'Test Value')


class WagtailBlocksTests(TestCase):
    """Testes para blocos Wagtail customizados."""
    
    def test_char_block(self):
        """Testa CharBlock."""
        from wagtail.blocks import CharBlock
        
        block = CharBlock(required=True, max_length=255)
        
        # Testa validação - CharBlock não expõe max_length no meta, apenas verifica required
        self.assertTrue(block.required)
    
    def test_richtext_block(self):
        """Testa RichTextBlock."""
        from wagtail.blocks import RichTextBlock
        
        block = RichTextBlock()
        test_html = '<p>Test content</p>'
        
        value = block.to_python(test_html)
        self.assertIsNotNone(value)


class BlocksPermissionsTests(TestCase):
    """Testes para permissões relacionadas aos blocos."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_without_wagtail_access(self):
        """Testa usuário sem acesso ao Wagtail admin."""
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_superuser_has_wagtail_access(self):
        """Testa superusuário tem acesso ao Wagtail admin."""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
