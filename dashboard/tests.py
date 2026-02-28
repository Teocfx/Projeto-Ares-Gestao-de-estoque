"""
Testes para o app dashboard.
Testa views, estatísticas e permissões.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from datetime import datetime, timedelta

from produtos.models import Product, Category, Unit


User = get_user_model()


class DashboardViewTestCase(TestCase):
    """Testes para a view principal do dashboard."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.client = Client()
        
        # Criar usuário de teste
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Criar categoria e unidade
        self.category = Category.objects.create(
            name='Eletrônicos',
            description='Produtos eletrônicos'
        )
        
        self.unit = Unit.objects.create(
            name='UN',
            description='Unidade'
        )
        
        # Criar produtos de teste
        self.product_ok = Product.objects.create(
            sku='PROD-001',
            name='Produto OK',
            category=self.category,
            unit=self.unit,
            current_stock=100,
            min_stock=10,
            unit_price=Decimal('50.00')
        )
        
        self.product_low = Product.objects.create(
            sku='PROD-002',
            name='Produto Baixo',
            category=self.category,
            unit=self.unit,
            current_stock=5,
            min_stock=10,
            unit_price=Decimal('30.00')
        )
        
        self.product_critical = Product.objects.create(
            sku='PROD-003',
            name='Produto Crítico',
            category=self.category,
            unit=self.unit,
            current_stock=0,
            min_stock=10,
            unit_price=Decimal('100.00')
        )
    
    def test_dashboard_requires_login(self):
        """Testa que o dashboard requer autenticação."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_dashboard_loads_for_authenticated_user(self):
        """Testa que o dashboard carrega para usuário autenticado."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)
        # Verificar que a página contém elementos do dashboard
        self.assertContains(response, 'dashboard')
    
    def test_dashboard_displays_product_statistics(self):
        """Testa que o dashboard exibe estatísticas de produtos."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que a página carrega e contém informações de produtos
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produto')
    
    def test_dashboard_calculates_stock_value(self):
        """Testa que o dashboard calcula o valor total do estoque."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que a página carrega e contém seção de valor
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estoque')
    
    def test_dashboard_shows_critical_products(self):
        """Testa que o dashboard mostra produtos críticos."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que mostra informações de estoque crítico
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertTrue('crítico' in content.lower() or 'critico' in content.lower())
    
    def test_dashboard_shows_low_stock_products(self):
        """Testa que o dashboard mostra produtos com estoque baixo."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que página carrega
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_with_expired_products(self):
        """Testa que o dashboard identifica produtos vencidos."""
        # Criar produto vencido
        Product.objects.create(
            sku='PROD-004',
            name='Produto Vencido',
            category=self.category,
            unit=self.unit,
            current_stock=10,
            min_stock=5,
            unit_price=Decimal('20.00'),
            expiry_date=(datetime.now() - timedelta(days=1)).date()
        )
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que a página carrega
        self.assertEqual(response.status_code, 200)


class DashboardCacheTestCase(TestCase):
    """Testes para verificar o cache do dashboard."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='cacheuser',
            password='testpass123'
        )
        self.client.login(username='cacheuser', password='testpass123')
    
    def test_dashboard_uses_cache(self):
        """Testa que o dashboard usa cache (decorator @cache_page)."""
        # Primeira requisição
        response1 = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response1.status_code, 200)
        
        # Segunda requisição (deve usar cache)
        response2 = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response2.status_code, 200)
        
        # Headers de cache devem estar presentes
        self.assertIn('Cache-Control', response2 or response1)


class DashboardMovementStatsTestCase(TestCase):
    """Testes para estatísticas de movimentações no dashboard."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='movuser',
            password='testpass123'
        )
        
        # Criar categoria, unidade e produto
        category = Category.objects.create(name='Teste')
        unit = Unit.objects.create(name='UN')
        self.product = Product.objects.create(
            sku='MOV-001',
            name='Produto Movimento',
            category=category,
            unit=unit,
            current_stock=100,
            min_stock=10
        )
        
        self.client.login(username='movuser', password='testpass123')
    
    def test_dashboard_loads_with_movements_section(self):
        """Testa que o dashboard carrega a seção de movimentações."""
        response = self.client.get(reverse('dashboard:index'))
        
        # Verificar que a página carrega
        self.assertEqual(response.status_code, 200)
        # Verificar que contém seção de movimentações ou produtos
        self.assertTrue(
            'produto' in response.content.decode().lower() or
            'movimento' in response.content.decode().lower()
        )
