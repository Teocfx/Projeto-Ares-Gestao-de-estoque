"""
Testes adicionais para o app produtos.
Complementa produtos/tests_api.py com testes de views, models e forms.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from decimal import Decimal
from datetime import datetime, timedelta

from produtos.models import Product, Category, Unit
from produtos.forms import ProductForm, CategoryForm, UnitForm


User = get_user_model()


class ProductModelTestCase(TestCase):
    """Testes para o modelo Product."""
    
    def setUp(self):
        """Configuração inicial."""
        self.category = Category.objects.create(
            name='Eletrônicos',
            description='Produtos eletrônicos'
        )
        
        self.unit = Unit.objects.create(
            name='UN',
            description='Unidade'
        )
    
    def test_product_creation(self):
        """Testa criação de produto."""
        product = Product.objects.create(
            sku='TEST-001',
            name='Produto Teste',
            category=self.category,
            unit=self.unit,
            current_stock=10,
            min_stock=5,
            unit_price=Decimal('100.00')
        )
        
        self.assertEqual(product.sku, 'TEST-001')
        self.assertEqual(product.name, 'Produto Teste')
        self.assertTrue(product.is_active)
    
    def test_product_str_representation(self):
        """Testa representação em string do produto."""
        product = Product.objects.create(
            sku='TEST-002',
            name='Produto String',
            category=self.category,
            unit=self.unit
        )
        
        # Verificar que a representação contém SKU e nome
        self.assertIn('TEST-002', str(product))
        self.assertIn('Produto String', str(product))
    
    def test_product_is_low_stock(self):
        """Testa método is_low_stock."""
        product = Product.objects.create(
            sku='TEST-003',
            name='Produto Baixo',
            category=self.category,
            unit=self.unit,
            current_stock=3,
            min_stock=10
        )
        
        self.assertTrue(product.has_low_stock())
    
    def test_product_is_not_low_stock(self):
        """Testa que produto com estoque OK não está baixo."""
        product = Product.objects.create(
            sku='TEST-004',
            name='Produto OK',
            category=self.category,
            unit=self.unit,
            current_stock=50,
            min_stock=10
        )
        
        self.assertFalse(product.has_low_stock())
    
    def test_product_is_expired(self):
        """Testa método is_expired."""
        yesterday = (datetime.now() - timedelta(days=1)).date()
        product = Product.objects.create(
            sku='TEST-005',
            name='Produto Vencido',
            category=self.category,
            unit=self.unit,
            expiry_date=yesterday
        )
        
        self.assertTrue(product.is_expired())
    
    def test_product_is_not_expired(self):
        """Testa que produto com data futura não está vencido."""
        tomorrow = (datetime.now() + timedelta(days=1)).date()
        product = Product.objects.create(
            sku='TEST-006',
            name='Produto Válido',
            category=self.category,
            unit=self.unit,
            expiry_date=tomorrow
        )
        
        self.assertFalse(product.is_expired())
    
    def test_product_without_expiry_date_not_expired(self):
        """Testa que produto sem data de validade não está vencido."""
        product = Product.objects.create(
            sku='TEST-007',
            name='Sem Validade',
            category=self.category,
            unit=self.unit
        )
        
        self.assertFalse(product.is_expired())
    
    def test_product_soft_delete(self):
        """Testa soft delete de produto."""
        product = Product.objects.create(
            sku='TEST-008',
            name='Para Deletar',
            category=self.category,
            unit=self.unit
        )
        
        product_id = product.id
        product.delete()
        
        # Produto foi removido das queries padrão
        self.assertFalse(Product.objects.filter(id=product_id).exists())
    
    def test_product_get_absolute_url(self):
        """Testa método get_absolute_url."""
        product = Product.objects.create(
            sku='TEST-009',
            name='Produto URL',
            category=self.category,
            unit=self.unit
        )
        
        url = product.get_absolute_url()
        self.assertEqual(url, reverse('produtos:detail', kwargs={'pk': product.pk}))


class CategoryModelTestCase(TestCase):
    """Testes para o modelo Category."""
    
    def test_category_creation(self):
        """Testa criação de categoria."""
        category = Category.objects.create(
            name='Alimentos',
            description='Produtos alimentícios'
        )
        
        self.assertEqual(category.name, 'Alimentos')
        self.assertEqual(str(category), 'Alimentos')
    
    def test_category_unique_name(self):
        """Testa que o nome da categoria é único."""
        Category.objects.create(name='Única')
        
        with self.assertRaises(Exception):
            Category.objects.create(name='Única')
    
    def test_category_get_absolute_url(self):
        """Testa método get_absolute_url."""
        category = Category.objects.create(name='Test Cat')
        url = category.get_absolute_url()
        
        self.assertIn('produtos', url)
        self.assertIn(str(category.pk), url)
    
    def test_category_search_description(self):
        """Testa propriedade search_description."""
        category = Category.objects.create(
            name='Test',
            description='Descrição teste'
        )
        
        self.assertEqual(category.search_description, 'Descrição teste')
    
    def test_category_search_description_fallback(self):
        """Testa fallback de search_description."""
        category = Category.objects.create(name='Test')
        self.assertIn('Test', category.search_description)


class UnitModelTestCase(TestCase):
    """Testes para o modelo Unit."""
    
    def test_unit_creation(self):
        """Testa criação de unidade."""
        unit = Unit.objects.create(
            name='KG',
            description='Quilograma'
        )
        
        self.assertEqual(unit.name, 'KG')
        self.assertEqual(str(unit), 'KG')
    
    def test_unit_unique_name(self):
        """Testa que o nome da unidade é único."""
        Unit.objects.create(name='L')
        
        with self.assertRaises(Exception):
            Unit.objects.create(name='L')


class ProductListViewTestCase(TestCase):
    """Testes para a view de listagem de produtos."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='listuser',
            password='testpass123'
        )
        
        # Adicionar permissão de visualizar produtos
        permission = Permission.objects.get(codename='view_product')
        self.user.user_permissions.add(permission)
        
        # Criar categoria e unidade
        self.category = Category.objects.create(name='Test')
        self.unit = Unit.objects.create(name='UN')
        
        # Criar produtos
        for i in range(15):
            Product.objects.create(
                sku=f'PROD-{i:03d}',
                name=f'Produto {i}',
                category=self.category,
                unit=self.unit,
                current_stock=10 * i,
                min_stock=5
            )
    
    def test_product_list_requires_login(self):
        """Testa que a lista de produtos requer login."""
        response = self.client.get(reverse('produtos:list'))
        self.assertEqual(response.status_code, 302)
    
    def test_product_list_requires_permission(self):
        """Testa que a lista de produtos requer permissão."""
        # Criar usuário sem permissão
        user_no_perm = User.objects.create_user(
            username='noperm',
            password='test123'
        )
        
        self.client.login(username='noperm', password='test123')
        response = self.client.get(reverse('produtos:list'))
        # Usuário sem permissão é redirecionado
        self.assertIn(response.status_code, [302, 403])
    
    def test_product_list_loads_successfully(self):
        """Testa que a lista de produtos carrega com sucesso."""
        self.client.login(username='listuser', password='testpass123')
        response = self.client.get(reverse('produtos:list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'produtos/product_list.html')
    
    def test_product_list_pagination(self):
        """Testa paginação da lista de produtos."""
        self.client.login(username='listuser', password='testpass123')
        response = self.client.get(reverse('produtos:list'))
        
        # Verifica paginação (20 por página)
        self.assertEqual(len(response.context['products']), 15)
    
    def test_product_list_search(self):
        """Testa busca na lista de produtos."""
        self.client.login(username='listuser', password='testpass123')
        response = self.client.get(reverse('produtos:list') + '?search=Produto 5')
        
        # Deve encontrar "Produto 5"
        self.assertContains(response, 'Produto 5')
    
    def test_product_list_filter_by_category(self):
        """Testa filtro por categoria."""
        self.client.login(username='listuser', password='testpass123')
        response = self.client.get(
            reverse('produtos:list') + f'?category={self.category.pk}'
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_product_list_filter_low_stock(self):
        """Testa filtro de produtos com estoque baixo."""
        self.client.login(username='listuser', password='testpass123')
        response = self.client.get(reverse('produtos:list') + '?low_stock=true')
        
        self.assertEqual(response.status_code, 200)


class ProductDetailViewTestCase(TestCase):
    """Testes para a view de detalhes do produto."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='detailuser',
            password='testpass123'
        )
        
        # Adicionar permissão
        permission = Permission.objects.get(codename='view_product')
        self.user.user_permissions.add(permission)
        
        # Criar produto
        category = Category.objects.create(name='Test')
        unit = Unit.objects.create(name='UN')
        self.product = Product.objects.create(
            sku='DETAIL-001',
            name='Produto Detalhe',
            description='Descrição detalhada',
            category=category,
            unit=unit,
            current_stock=50,
            min_stock=10,
            unit_price=Decimal('99.99')
        )
    
    def test_product_detail_requires_login(self):
        """Testa que os detalhes requerem login."""
        url = reverse('produtos:detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
    
    def test_product_detail_loads_successfully(self):
        """Testa que os detalhes carregam com sucesso."""
        self.client.login(username='detailuser', password='testpass123')
        url = reverse('produtos:detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produto Detalhe')
        self.assertContains(response, 'DETAIL-001')
    
    def test_product_detail_shows_price(self):
        """Testa que o preço é exibido nos detalhes."""
        self.client.login(username='detailuser', password='testpass123')
        url = reverse('produtos:detail', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        
        # Verificar que preço aparece (formato BR: 99,99)
        self.assertContains(response, '99,99')


class ProductFormTestCase(TestCase):
    """Testes para o formulário de produto."""
    
    def setUp(self):
        """Configuração inicial."""
        self.category = Category.objects.create(name='Test')
        self.unit = Unit.objects.create(name='UN')
    
    def test_product_form_valid_data(self):
        """Testa formulário com dados válidos."""
        form_data = {
            'sku': 'FORM-001',
            'name': 'Produto Formulário',
            'description': 'Descrição',
            'category': self.category.pk,
            'unit': self.unit.pk,
            'current_stock': 10,
            'min_stock': 5,
            'unit_price': Decimal('50.00')
        }
        
        form = ProductForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_product_form_missing_required_fields(self):
        """Testa formulário sem campos obrigatórios."""
        form_data = {
            'sku': 'FORM-002'
            # Faltando name, category, unit
        }
        
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('category', form.errors)
    
    def test_product_form_duplicate_sku(self):
        """Testa formulário com SKU duplicado."""
        # Criar produto existente
        Product.objects.create(
            sku='DUP-001',
            name='Existente',
            category=self.category,
            unit=self.unit
        )
        
        # Tentar criar outro com mesmo SKU
        form_data = {
            'sku': 'DUP-001',
            'name': 'Novo',
            'category': self.category.pk,
            'unit': self.unit.pk
        }
        
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_product_form_negative_stock(self):
        """Testa formulário com estoque negativo."""
        form_data = {
            'sku': 'NEG-001',
            'name': 'Negativo',
            'category': self.category.pk,
            'unit': self.unit.pk,
            'current_stock': -10  # Negativo
        }
        
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())


class CategoryFormTestCase(TestCase):
    """Testes para o formulário de categoria."""
    
    def test_category_form_valid_data(self):
        """Testa formulário com dados válidos."""
        form_data = {
            'name': 'Nova Categoria',
            'description': 'Descrição da categoria'
        }
        
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_category_form_missing_name(self):
        """Testa formulário sem nome."""
        form_data = {
            'description': 'Só descrição'
        }
        
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ProductCreateViewTestCase(TestCase):
    """Testes para a view de criação de produto."""
    
    def setUp(self):
        """Configuração inicial."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='createuser',
            password='testpass123'
        )
        
        # Adicionar permissões
        add_perm = Permission.objects.get(codename='add_product')
        self.user.user_permissions.add(add_perm)
        
        self.category = Category.objects.create(name='Test')
        self.unit = Unit.objects.create(name='UN')
    
    def test_product_create_requires_permission(self):
        """Testa que criação requer permissão."""
        user_no_perm = User.objects.create_user(
            username='noperm2',
            password='test123'
        )
        
        self.client.login(username='noperm2', password='test123')
        response = self.client.get(reverse('produtos:create'))
        # Usuário sem permissão é redirecionado
        self.assertIn(response.status_code, [302, 403])
    
    def test_product_create_form_displays(self):
        """Testa que o formulário de criação é exibido."""
        self.client.login(username='createuser', password='testpass123')
        response = self.client.get(reverse('produtos:create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_product_create_successful(self):
        """Testa criação bem-sucedida de produto."""
        self.client.login(username='createuser', password='testpass123')
        
        post_data = {
            'sku': 'CREATE-001',
            'name': 'Novo Produto',
            'category': self.category.pk,
            'unit': self.unit.pk,
            'current_stock': 100,
            'min_stock': 10,
            'unit_price': '50.00'
        }
        
        response = self.client.post(reverse('produtos:create'), data=post_data)
        
        # Deve redirecionar após sucesso
        self.assertEqual(response.status_code, 302)
        
        # Verificar que o produto foi criado
        self.assertTrue(Product.objects.filter(sku='CREATE-001').exists())
