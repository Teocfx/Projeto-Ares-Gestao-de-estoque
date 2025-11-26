"""
Testes para o módulo de relatórios.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from produtos.models import Product, Category, Unit
from movimentacoes.models import InventoryMovement
from .models import ReportGeneration, ReportType
from .pdf_generator import PDFGenerator

User = get_user_model()


class ReportIndexViewTests(TestCase):
    """Testes para a view de índice de relatórios."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Criar dados de teste
        self.category = Category.objects.create(
            name='Categoria Teste',
            is_active=True
        )
        self.unit = Unit.objects.create(
            name='UN',
            abbreviation='un',
            is_active=True
        )
    
    def test_index_view_requires_login(self):
        """Testa se a view requer autenticação."""
        self.client.logout()
        response = self.client.get(reverse('relatorios:index'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_index_view_renders_correct_template(self):
        """Testa se a view renderiza o template correto."""
        response = self.client.get(reverse('relatorios:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'relatorios/index.html')
    
    def test_index_view_displays_statistics(self):
        """Testa se a view exibe as estatísticas corretas."""
        # Criar produtos
        Product.objects.create(
            name='Produto 1',
            sku='SKU001',
            category=self.category,
            unit=self.unit,
            current_stock=5,
            min_stock=10,
            price=Decimal('10.00'),
            is_active=True
        )
        Product.objects.create(
            name='Produto 2',
            sku='SKU002',
            category=self.category,
            unit=self.unit,
            current_stock=20,
            min_stock=10,
            price=Decimal('15.00'),
            is_active=True
        )
        
        response = self.client.get(reverse('relatorios:index'))
        self.assertEqual(response.context['total_products'], 2)
        self.assertEqual(response.context['low_stock_products'], 1)


class EstoqueReportTests(TestCase):
    """Testes para o relatório de estoque."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='Unidade', abbreviation='un', is_active=True)
        
        # Criar produtos com diferentes status
        self.product_critical = Product.objects.create(
            name='Produto Crítico',
            sku='CRIT001',
            category=self.category,
            unit=self.unit,
            current_stock=0,
            min_stock=10,
            price=Decimal('50.00'),
            is_active=True
        )
        self.product_low = Product.objects.create(
            name='Produto Baixo',
            sku='LOW001',
            category=self.category,
            unit=self.unit,
            current_stock=5,
            min_stock=10,
            price=Decimal('30.00'),
            is_active=True
        )
        self.product_ok = Product.objects.create(
            name='Produto OK',
            sku='OK001',
            category=self.category,
            unit=self.unit,
            current_stock=50,
            min_stock=10,
            price=Decimal('20.00'),
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
        self.assertEqual(stats['ok_count'], 1)
    
    def test_estoque_filter_by_status(self):
        """Testa filtro por status de estoque."""
        response = self.client.get(reverse('relatorios:estoque') + '?status=critical')
        products = response.context['products']
        
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().name, 'Produto Crítico')
    
    def test_estoque_filter_by_category(self):
        """Testa filtro por categoria."""
        response = self.client.get(
            reverse('relatorios:estoque') + f'?category={self.category.id}'
        )
        products = response.context['products']
        
        self.assertEqual(products.count(), 3)
    
    def test_estoque_pdf_download(self):
        """Testa download do PDF de estoque."""
        response = self.client.get(reverse('relatorios:download_estoque_pdf'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])


class MovimentacoesReportTests(TestCase):
    """Testes para o relatório de movimentações."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='Unidade', abbreviation='un', is_active=True)
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=100,
            min_stock=10,
            price=Decimal('25.00'),
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
    
    def test_movimentacoes_filter_by_type(self):
        """Testa filtro por tipo de movimentação."""
        response = self.client.get(
            reverse('relatorios:movimentacoes') + '?type=entrada'
        )
        movements = response.context['movements']
        
        self.assertEqual(movements.count(), 1)
        self.assertEqual(movements.first().type, InventoryMovement.ENTRADA)
    
    def test_movimentacoes_filter_by_date(self):
        """Testa filtro por data."""
        today = timezone.now().date()
        response = self.client.get(
            reverse('relatorios:movimentacoes') +
            f'?date_from={today}&date_to={today}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_movimentacoes_pdf_download(self):
        """Testa download do PDF de movimentações."""
        response = self.client.get(reverse('relatorios:download_movimentacoes_pdf'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


class PDFGeneratorTests(TestCase):
    """Testes para o gerador de PDF."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='Unidade', abbreviation='un', is_active=True)
        
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=50,
            min_stock=10,
            price=Decimal('20.00'),
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
    
    def test_pdf_generation_with_products(self):
        """Testa geração de PDF com produtos."""
        pdf_gen = PDFGenerator(
            title="Relatório de Estoque",
            subtitle="Teste",
            author="Test User"
        )
        
        context = {
            'products': [self.product],
            'stats': {
                'total_products': 1,
                'critical_count': 0,
                'low_count': 0,
                'ok_count': 1,
                'total_value': Decimal('1000.00')
            }
        }
        
        pdf_bytes = pdf_gen.generate_pdf('relatorios/pdf/estoque.html', context)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 0)
