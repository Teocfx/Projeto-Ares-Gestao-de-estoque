"""
Testes para o módulo de movimentações de estoque.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from produtos.models import Product, Category, Unit
from .models import InventoryMovement
from .forms import InventoryMovementForm

User = get_user_model()


class InventoryMovementModelTests(TestCase):
    """Testes para o modelo InventoryMovement."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            name='Categoria Teste',
            is_active=True
        )
        self.unit = Unit.objects.create(
            name='Unidade',
            abbreviation='un',
            is_active=True
        )
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
    
    def test_create_entrada_movement(self):
        """Testa criação de movimentação de entrada."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=50,
            user=self.user,
            notes='Entrada teste'
        )
        
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.type, InventoryMovement.ENTRADA)
        self.assertEqual(movement.quantity, 50)
        self.assertEqual(movement.user, self.user)
    
    def test_create_saida_movement(self):
        """Testa criação de movimentação de saída."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.SAIDA,
            quantity=20,
            user=self.user,
            notes='Saída teste'
        )
        
        self.assertEqual(movement.type, InventoryMovement.SAIDA)
        self.assertEqual(movement.quantity, 20)
    
    def test_create_ajuste_movement(self):
        """Testa criação de movimentação de ajuste."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.AJUSTE,
            quantity=5,
            user=self.user,
            notes='Ajuste teste'
        )
        
        self.assertEqual(movement.type, InventoryMovement.AJUSTE)
        self.assertEqual(movement.quantity, 5)
    
    def test_movement_str_representation(self):
        """Testa a representação string da movimentação."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=30,
            user=self.user
        )
        
        expected = f"ENTRADA - {self.product.name} - 30"
        self.assertEqual(str(movement), expected)
    
    def test_movement_with_document(self):
        """Testa movimentação com documento."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=40,
            user=self.user,
            document='NF-12345',
            notes='Entrada com nota fiscal'
        )
        
        self.assertEqual(movement.document, 'NF-12345')
    
    def test_movement_timestamps(self):
        """Testa se os timestamps são criados automaticamente."""
        movement = InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=10,
            user=self.user
        )
        
        self.assertIsNotNone(movement.created_at)
        self.assertIsNotNone(movement.updated_at)


class MovementListViewTests(TestCase):
    """Testes para a view de listagem de movimentações."""
    
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
            price=Decimal('20.00'),
            is_active=True
        )
        
        # Criar movimentações de teste
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=50,
            user=self.user
        )
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.SAIDA,
            quantity=20,
            user=self.user
        )
    
    def test_list_view_requires_login(self):
        """Testa se a view requer autenticação."""
        self.client.logout()
        response = self.client.get(reverse('movimentacoes:list'))
        self.assertEqual(response.status_code, 302)
    
    def test_list_view_loads(self):
        """Testa se a view carrega corretamente."""
        response = self.client.get(reverse('movimentacoes:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimentacoes/list.html')
    
    def test_list_view_shows_movements(self):
        """Testa se a view exibe as movimentações."""
        response = self.client.get(reverse('movimentacoes:list'))
        self.assertEqual(len(response.context['movements']), 2)
    
    def test_list_view_filter_by_type(self):
        """Testa filtro por tipo de movimentação."""
        response = self.client.get(reverse('movimentacoes:list') + '?type=ENTRADA')
        movements = response.context['movements']
        
        self.assertEqual(movements.count(), 1)
        self.assertEqual(movements.first().type, InventoryMovement.ENTRADA)
    
    def test_list_view_search(self):
        """Testa busca por produto."""
        response = self.client.get(
            reverse('movimentacoes:list') + '?search=Produto Teste'
        )
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.context['movements']), 0)


class MovementCreateViewTests(TestCase):
    """Testes para a view de criação de movimentações."""
    
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
            price=Decimal('20.00'),
            is_active=True
        )
    
    def test_create_view_loads(self):
        """Testa se a view de criação carrega."""
        response = self.client.get(reverse('movimentacoes:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'movimentacoes/form.html')
    
    def test_create_entrada_success(self):
        """Testa criação bem-sucedida de entrada."""
        data = {
            'product': self.product.id,
            'type': InventoryMovement.ENTRADA,
            'quantity': 50,
            'notes': 'Entrada teste'
        }
        
        response = self.client.post(reverse('movimentacoes:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InventoryMovement.objects.count(), 1)
    
    def test_create_saida_success(self):
        """Testa criação bem-sucedida de saída."""
        data = {
            'product': self.product.id,
            'type': InventoryMovement.SAIDA,
            'quantity': 20,
            'notes': 'Saída teste'
        }
        
        response = self.client.post(reverse('movimentacoes:create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(InventoryMovement.objects.count(), 1)


class InventoryMovementFormTests(TestCase):
    """Testes para o formulário de movimentações."""
    
    def setUp(self):
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='Unidade', abbreviation='un', is_active=True)
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=100,
            min_stock=10,
            price=Decimal('20.00'),
            is_active=True
        )
    
    def test_form_valid_data(self):
        """Testa formulário com dados válidos."""
        form_data = {
            'product': self.product.id,
            'type': InventoryMovement.ENTRADA,
            'quantity': 50,
            'notes': 'Entrada teste'
        }
        
        form = InventoryMovementForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalid_quantity(self):
        """Testa formulário com quantidade inválida."""
        form_data = {
            'product': self.product.id,
            'type': InventoryMovement.ENTRADA,
            'quantity': -10,  # Quantidade negativa
            'notes': 'Entrada teste'
        }
        
        form = InventoryMovementForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_missing_product(self):
        """Testa formulário sem produto."""
        form_data = {
            'type': InventoryMovement.ENTRADA,
            'quantity': 50,
            'notes': 'Entrada teste'
        }
        
        form = InventoryMovementForm(data=form_data)
        self.assertFalse(form.is_valid())


class MovementStatisticsTests(TestCase):
    """Testes para estatísticas de movimentações."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Categoria', is_active=True)
        self.unit = Unit.objects.create(name='Unidade', abbreviation='un', is_active=True)
        self.product = Product.objects.create(
            name='Produto Teste',
            sku='TEST001',
            category=self.category,
            unit=self.unit,
            current_stock=100,
            min_stock=10,
            price=Decimal('20.00'),
            is_active=True
        )
    
    def test_count_by_type(self):
        """Testa contagem por tipo de movimentação."""
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=50,
            user=self.user
        )
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.ENTRADA,
            quantity=30,
            user=self.user
        )
        InventoryMovement.objects.create(
            product=self.product,
            type=InventoryMovement.SAIDA,
            quantity=20,
            user=self.user
        )
        
        entradas = InventoryMovement.objects.filter(type=InventoryMovement.ENTRADA).count()
        saidas = InventoryMovement.objects.filter(type=InventoryMovement.SAIDA).count()
        
        self.assertEqual(entradas, 2)
        self.assertEqual(saidas, 1)
