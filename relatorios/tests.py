"""
Testes para o módulo de relatórios.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from produtos.models import Product, Category, Unit
from movimentacoes.models import InventoryMovement
from .models import ReportGeneration
from .pdf_generator import PDFGenerator

User = get_user_model()


class ReportIndexViewTests(TestCase):
    """Testes para a view de índice de relatórios."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_staff=True  # Tornar staff para ter acesso aos relatórios
        )
        # Adicionar todas as permissões de relatórios
        content_type = ContentType.objects.get_for_model(ReportGeneration)
        permissions = Permission.objects.filter(content_type=content_type)
        self.user.user_permissions.add(*permissions)
        
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dados de teste
        self.category = Category.objects.create(
            name='Categoria Teste'
        )
        self.unit = Unit.objects.create(
            name='UN',
            description='Unidade'
        )
    
    def test_index_view_requires_login(self):
        """Testa se a view requer autenticação."""
        self.client.logout()
        response = self.client.get(reverse('relatorios:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


@override_settings(
    STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
)
class EstoqueReportTests(TestCase):
    """Testes para o relatório de estoque."""
    
    def setUp(self):
        self.client = Client()
        # Criar superuser para ter todas as permissões
        self.user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='UN', description='Unidade')
        
        # Criar produtos com diferentes status
        self.product_critical = Product.objects.create(
            name='Produto Crítico',
            sku='CRIT001',
            category=self.category,
            unit=self.unit,
            current_stock=0,
            min_stock=10,
            unit_price=Decimal('50.00'),
            is_active=True
        )
        self.product_low = Product.objects.create(
            name='Produto Baixo',
            sku='LOW001',
            category=self.category,
            unit=self.unit,
            current_stock=5,
            min_stock=10,
            unit_price=Decimal('30.00'),
            is_active=True
        )
        self.product_ok = Product.objects.create(
            name='Produto OK',
            sku='OK001',
            category=self.category,
            unit=self.unit,
            current_stock=50,
            min_stock=10,
            unit_price=Decimal('20.00'),
            is_active=True
        )
    
    def test_estoque_view_loads(self):
        """Testa se a view de estoque carrega corretamente."""
        response = self.client.get(reverse('relatorios:estoque'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relatorios/estoque.html')
    
    def test_estoque_view_statistics(self):
        """Testa se as estatísticas são calculadas corretamente."""
        response = self.client.get(reverse('relatorios:estoque'))
        stats = response.context['stats']
        
        self.assertEqual(stats['total_products'], 3)
        self.assertEqual(stats['critical_count'], 1)
        self.assertEqual(stats['low_count'], 1)
        # View não retorna 'ok_count', apenas total, critical e low
        self.assertIn('total_value', stats)
    
    def test_estoque_filter_by_category(self):
        """Testa filtro por categoria."""
        response = self.client.get(
            reverse('relatorios:estoque') + f'?category={self.category.id}'
        )
        products = response.context['products']
        
        self.assertEqual(len(products), 3)


@override_settings(
    STORAGES={"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
)
class MovimentacoesReportTests(TestCase):
    """Testes para o relatório de movimentações."""
    
    def setUp(self):
        self.client = Client()
        # Criar superuser para ter todas as permissões
        self.user = User.objects.create_superuser(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='UN', description='Unidade')
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=100,
            min_stock=10,
            unit_price=Decimal('25.00'),
            is_active=True
        )
        
        # Criar movimentações
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=50,
            user=self.user,
            notes='Entrada teste'
        )
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.SAIDA,
            quantity=20,
            user=self.user,
            notes='Saída teste'
        )
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.AJUSTE,
            quantity=5,
            user=self.user,
            notes='Ajuste teste'
        )
    
    def test_movimentacoes_view_loads(self):
        """Testa se a view de movimentações carrega."""
        response = self.client.get(reverse('relatorios:movimentacoes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relatorios/movimentacoes.html')
    
    def test_movimentacoes_statistics(self):
        """Testa se as estatísticas são calculadas corretamente."""
        response = self.client.get(reverse('relatorios:movimentacoes'))
        stats = response.context['stats']
        
        self.assertEqual(stats['total_movements'], 3)
        self.assertEqual(stats['entradas'], 1)
        self.assertEqual(stats['saidas'], 1)
        self.assertEqual(stats['ajustes'], 1)
    
    def test_movimentacoes_filter_by_date(self):
        """Testa filtro por data."""
        today = timezone.now().date()
        response = self.client.get(
            reverse('relatorios:movimentacoes') +
            f'?date_from={today}&date_to={today}'
        )
        self.assertEqual(response.status_code, 200)


class PDFGeneratorTests(TestCase):
    """Testes para o gerador de PDF."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='UN', description='Unidade')
        
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=50,
            min_stock=10,
            unit_price=Decimal('20.00'),
            is_active=True
        )
    
    def test_pdf_generator_initialization(self):
        """Testa inicialização do gerador de PDF."""
        pdf_gen = PDFGenerator(
            title="Relatório Teste",
            subtitle="Subtítulo",
            author="Test User"
        )
        
        self.assertEqual(pdf_gen.title, "Relatório Teste")
        self.assertEqual(pdf_gen.subtitle, "Subtítulo")
        self.assertEqual(pdf_gen.author, "Test User")


