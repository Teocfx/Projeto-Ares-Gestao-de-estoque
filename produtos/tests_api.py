"""
Testes automatizados para API REST - Produtos.

pytest -v produtos/tests_api.py
pytest --cov=produtos produtos/tests_api.py
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from produtos.models import Category, Unit, Product
from core.models import PerfilUsuario, PerfilAcesso

User = get_user_model()


@pytest.fixture
def api_client():
    """Cliente da API."""
    return APIClient()


@pytest.fixture
def admin_user(db):
    """Usuário administrador."""
    user = User.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='testpass123',
        is_staff=True
    )
    PerfilUsuario.objects.create(
        user=user,
        perfil=PerfilAcesso.REPRESENTANTE_LEGAL,
        ativo=True
    )
    return user


@pytest.fixture
def basic_user(db):
    """Usuário operador."""
    user = User.objects.create_user(
        username='operador',
        email='operador@test.com',
        password='testpass123'
    )
    PerfilUsuario.objects.create(
        user=user,
        perfil=PerfilAcesso.OPERADOR,
        ativo=True
    )
    return user


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Cliente autenticado como admin."""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def category(db):
    """Categoria de teste."""
    return Category.objects.create(
        name='Eletrônicos',
        description='Produtos eletrônicos'
    )


@pytest.fixture
def unit(db):
    """Unidade de medida de teste."""
    return Unit.objects.create(
        name='UN',
        description='Unidade'
    )


@pytest.fixture
def product(db, category, unit):
    """Produto de teste."""
    return Product.objects.create(
        sku='PROD-001',
        name='Mouse Logitech',
        description='Mouse sem fio',
        category=category,
        unit=unit,
        current_stock=Decimal('10.00'),
        min_stock=Decimal('5.00'),
        unit_price=Decimal('89.90')
    )


class TestJWTAuthentication:
    """Testes de autenticação JWT."""
    
    def test_obtain_token_success(self, api_client, admin_user):
        """T06.1 - Obter JWT token com credenciais válidas."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': 'admin',
            'password': 'testpass123'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_obtain_token_invalid_credentials(self, api_client, admin_user):
        """Obter JWT token com credenciais inválidas."""
        response = api_client.post('/api/v1/auth/token/', {
            'username': 'admin',
            'password': 'wrongpass'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_access_without_token(self, api_client):
        """T06.4 - Acessar endpoint sem token."""
        response = api_client.get('/api/v1/products/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCategoryAPI:
    """Testes da API de Categorias."""
    
    def test_list_categories(self, authenticated_client, category):
        """Listar categorias."""
        response = authenticated_client.get('/api/v1/categories/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == 'Eletrônicos'
    
    def test_create_category(self, authenticated_client):
        """Criar categoria."""
        data = {
            'name': 'Escritório',
            'description': 'Material de escritório'
        }
        response = authenticated_client.post('/api/v1/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='Escritório').exists()
    
    def test_create_category_duplicate_name(self, authenticated_client, category):
        """Criar categoria com nome duplicado."""
        data = {
            'name': 'Eletrônicos',
            'description': 'Duplicado'
        }
        response = authenticated_client.post('/api/v1/categories/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProductAPI:
    """Testes da API de Produtos."""
    
    def test_list_products(self, authenticated_client, product):
        """T06.5 - Listar produtos via API."""
        response = authenticated_client.get('/api/v1/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['sku'] == 'PROD-001'
    
    def test_create_product(self, authenticated_client, category, unit):
        """T06.6 - Criar produto via API."""
        data = {
            'sku': 'PROD-002',
            'name': 'Teclado Mecânico',
            'description': 'Teclado gamer RGB',
            'category_id': category.id,
            'unit_id': unit.id,
            'current_stock': '20.00',
            'min_stock': '10.00',
            'unit_price': '450.00'
        }
        response = authenticated_client.post('/api/v1/products/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(sku='PROD-002').exists()
    
    def test_update_product(self, authenticated_client, product):
        """T06.7 - Atualizar produto via API."""
        data = {
            'name': 'Mouse Logitech MX Master',
            'category_id': product.category.id,
            'unit_id': product.unit.id
        }
        response = authenticated_client.patch(
            f'/api/v1/products/{product.id}/',
            data
        )
        
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.name == 'Mouse Logitech MX Master'
    
    def test_delete_product(self, authenticated_client, product):
        """T06.8 - Remover produto via API (soft delete)."""
        response = authenticated_client.delete(f'/api/v1/products/{product.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        product.refresh_from_db()
        assert not product.is_active
    
    def test_filter_products_by_category(self, authenticated_client, product, category):
        """T06.9 - Filtrar produtos por categoria."""
        response = authenticated_client.get(
            f'/api/v1/products/?category={category.id}'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_low_stock_products(self, authenticated_client, product):
        """T06.14 - Produtos com estoque baixo."""
        # Reduzir estoque para abaixo do mínimo
        product.current_stock = Decimal('3.00')
        product.save()
        
        response = authenticated_client.get('/api/v1/products/low_stock/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
    
    def test_product_stats(self, authenticated_client, product):
        """T06.13 - Estatísticas de produtos."""
        response = authenticated_client.get('/api/v1/products/stats/')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'total_products' in response.data
        assert response.data['total_products'] == 1


class TestMovementAPI:
    """Testes da API de Movimentações."""
    
    def test_create_entry_movement(self, authenticated_client, product):
        """T06.11 - Criar movimentação de entrada."""
        initial_stock = product.current_stock
        
        data = {
            'product_id': product.id,
            'type': 'ENTRADA',
            'quantity': '50.00',
            'document': 'NF-12345',
            'notes': 'Compra de fornecedor'
        }
        response = authenticated_client.post('/api/v1/movements/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        product.refresh_from_db()
        assert product.current_stock == initial_stock + Decimal('50.00')
    
    def test_create_exit_movement(self, authenticated_client, product):
        """Criar movimentação de saída."""
        initial_stock = product.current_stock
        
        data = {
            'product_id': product.id,
            'type': 'SAIDA',
            'quantity': '5.00',
            'notes': 'Venda'
        }
        response = authenticated_client.post('/api/v1/movements/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        product.refresh_from_db()
        assert product.current_stock == initial_stock - Decimal('5.00')
    
    def test_exit_insufficient_stock(self, authenticated_client, product):
        """T03.3 - Saída com estoque insuficiente."""
        data = {
            'product_id': product.id,
            'type': 'SAIDA',
            'quantity': '1000.00',
            'notes': 'Tentativa de saída excessiva'
        }
        response = authenticated_client.post('/api/v1/movements/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'quantity' in response.data
    
    def test_bulk_create_movements(self, authenticated_client, product, category, unit):
        """T06.12 - Bulk create movimentações."""
        # Criar segundo produto
        product2 = Product.objects.create(
            sku='PROD-003',
            name='Teclado',
            category=category,
            unit=unit,
            current_stock=Decimal('20.00'),
            min_stock=Decimal('5.00')
        )
        
        data = {
            'movements': [
                {
                    'product_id': product.id,
                    'type': 'ENTRADA',
                    'quantity': '10.00'
                },
                {
                    'product_id': product2.id,
                    'type': 'SAIDA',
                    'quantity': '5.00'
                }
            ]
        }
        response = authenticated_client.post('/api/v1/movements/bulk_create/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['count'] == 2


class TestPermissions:
    """Testes de permissões da API."""
    
    def test_operador_cannot_create_category(self, api_client, basic_user, db):
        """T04.4 - Operador tentando criar categoria."""
        api_client.force_authenticate(user=basic_user)
        
        data = {'name': 'Nova Categoria'}
        response = api_client.post('/api/v1/categories/', data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_admin_can_create_category(self, authenticated_client):
        """Admin pode criar categoria."""
        data = {'name': 'Nova Categoria'}
        response = authenticated_client.post('/api/v1/categories/', data)
        
        assert response.status_code == status.HTTP_201_CREATED


class TestPagination:
    """Testes de paginação."""
    
    def test_pagination_page_size(self, authenticated_client, category, unit, db):
        """T06.10 - Paginação da API."""
        # Criar 25 produtos
        for i in range(25):
            Product.objects.create(
                sku=f'PROD-{i:03d}',
                name=f'Produto {i}',
                category=category,
                unit=unit,
                current_stock=Decimal('10.00'),
                min_stock=Decimal('5.00')
            )
        
        response = authenticated_client.get('/api/v1/products/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 25
        assert len(response.data['results']) == 20  # Page size padrão
        assert 'next' in response.data
    
    def test_pagination_second_page(self, authenticated_client, category, unit, db):
        """Segunda página da paginação."""
        for i in range(25):
            Product.objects.create(
                sku=f'PROD-{i:03d}',
                name=f'Produto {i}',
                category=category,
                unit=unit,
                current_stock=Decimal('10.00'),
                min_stock=Decimal('5.00')
            )
        
        response = authenticated_client.get('/api/v1/products/?page=2')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        assert 'previous' in response.data


class TestValidation:
    """Testes de validação."""
    
    def test_create_product_missing_required_fields(self, authenticated_client):
        """T02.3 - Criar produto sem campos obrigatórios."""
        data = {
            'name': 'Produto Incompleto'
        }
        response = authenticated_client.post('/api/v1/products/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sku' in response.data
    
    def test_create_product_duplicate_sku(self, authenticated_client, product):
        """T02.2 - Criar produto com SKU duplicado."""
        data = {
            'sku': 'PROD-001',  # SKU já existe
            'name': 'Produto Duplicado',
            'category_id': product.category.id,
            'unit_id': product.unit.id
        }
        response = authenticated_client.post('/api/v1/products/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'sku' in response.data
    
    def test_negative_price(self, authenticated_client, category, unit):
        """T02.12 - Validar campos numéricos."""
        data = {
            'sku': 'PROD-NEG',
            'name': 'Produto Negativo',
            'category_id': category.id,
            'unit_id': unit.id,
            'unit_price': '-10.00'
        }
        response = authenticated_client.post('/api/v1/products/', data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
