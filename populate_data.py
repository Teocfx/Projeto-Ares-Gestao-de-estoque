#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo.
Execute com: python manage.py shell < populate_data.py
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siteares.settings.development')
django.setup()

from produtos.models import Category, Unit, Product
from movimentacoes.models import InventoryMovement
from django.contrib.auth import get_user_model

User = get_user_model()

# Criar usuário admin se não existir
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✓ Usuário admin criado")

# Criar categorias
categorias_data = [
    {'name': 'Alimentos', 'description': 'Produtos alimentícios em geral'},
    {'name': 'Bebidas', 'description': 'Bebidas alcoólicas e não-alcoólicas'},
    {'name': 'Higiene', 'description': 'Produtos de higiene pessoal'},
    {'name': 'Limpeza', 'description': 'Produtos de limpeza doméstica'},
    {'name': 'Eletrônicos', 'description': 'Aparelhos e equipamentos eletrônicos'},
]

categorias = {}
for cat_data in categorias_data:
    categoria, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categorias[cat_data['name']] = categoria
    if created:
        print(f"✓ Categoria criada: {categoria.name}")

# Criar unidades
unidades_data = [
    {'name': 'UN', 'description': 'Unidade'},
    {'name': 'KG', 'description': 'Quilograma'},
    {'name': 'L', 'description': 'Litro'},
    {'name': 'ML', 'description': 'Mililitro'},
    {'name': 'CX', 'description': 'Caixa'},
    {'name': 'PC', 'description': 'Peça'},
]

unidades = {}
for unit_data in unidades_data:
    unidade, created = Unit.objects.get_or_create(
        name=unit_data['name'],
        defaults={'description': unit_data['description']}
    )
    unidades[unit_data['name']] = unidade
    if created:
        print(f"✓ Unidade criada: {unidade.name}")

# Criar produtos
produtos_data = [
    {
        'sku': 'ALM001',
        'name': 'Arroz Integral 1kg',
        'description': 'Arroz integral tipo 1, embalagem 1kg',
        'category': 'Alimentos',
        'unit': 'UN',
        'min_stock': 10,
        'current_stock': 25,
        'unit_price': 8.90,
        'expiry_date': date.today() + timedelta(days=180),
    },
    {
        'sku': 'ALM002',
        'name': 'Feijão Carioca 1kg',
        'description': 'Feijão carioca tipo 1, embalagem 1kg',
        'category': 'Alimentos',
        'unit': 'UN',
        'min_stock': 8,
        'current_stock': 3,  # Estoque crítico
        'unit_price': 6.90,
        'expiry_date': date.today() + timedelta(days=365),
    },
    {
        'sku': 'BEB001',
        'name': 'Refrigerante Cola 2L',
        'description': 'Refrigerante sabor cola, garrafa 2 litros',
        'category': 'Bebidas',
        'unit': 'UN',
        'min_stock': 15,
        'current_stock': 0,  # Estoque zerado
        'unit_price': 5.99,
        'expiry_date': date.today() + timedelta(days=90),
    },
    {
        'sku': 'BEB002',
        'name': 'Água Mineral 500ml',
        'description': 'Água mineral natural, garrafa 500ml',
        'category': 'Bebidas',
        'unit': 'UN',
        'min_stock': 50,
        'current_stock': 120,
        'unit_price': 2.50,
        'expiry_date': date.today() + timedelta(days=730),
    },
    {
        'sku': 'HIG001',
        'name': 'Shampoo Anticaspa 400ml',
        'description': 'Shampoo anticaspa para uso diário',
        'category': 'Higiene',
        'unit': 'UN',
        'min_stock': 5,
        'current_stock': 8,
        'unit_price': 18.90,
        'expiry_date': date.today() + timedelta(days=1095),
    },
    {
        'sku': 'LIM001',
        'name': 'Detergente Neutro 500ml',
        'description': 'Detergente neutro para louças',
        'category': 'Limpeza',
        'unit': 'UN',
        'min_stock': 12,
        'current_stock': 45,
        'unit_price': 4.50,
        'expiry_date': date.today() + timedelta(days=1460),
    },
    {
        'sku': 'ELE001',
        'name': 'Carregador USB-C',
        'description': 'Carregador rápido USB-C 25W',
        'category': 'Eletrônicos',
        'unit': 'PC',
        'min_stock': 3,
        'current_stock': 12,
        'unit_price': 39.90,
        'expiry_date': None,  # Sem vencimento
    },
    {
        'sku': 'ALM003',
        'name': 'Leite UHT Integral 1L',
        'description': 'Leite UHT integral, embalagem longa vida',
        'category': 'Alimentos',
        'unit': 'UN',
        'min_stock': 20,
        'current_stock': 15,  # Estoque baixo
        'unit_price': 5.90,
        'expiry_date': date.today() + timedelta(days=30),  # Vence em breve
    },
]

produtos = {}
for prod_data in produtos_data:
    produto, created = Product.objects.get_or_create(
        sku=prod_data['sku'],
        defaults={
            'name': prod_data['name'],
            'description': prod_data['description'],
            'category': categorias[prod_data['category']],
            'unit': unidades[prod_data['unit']],
            'min_stock': Decimal(str(prod_data['min_stock'])),
            'current_stock': Decimal(str(prod_data['current_stock'])),
            'cost_price': Decimal(str(prod_data['cost_price'])),
            'sale_price': Decimal(str(prod_data['sale_price'])),
            'expiry_date': prod_data['expiry_date'],
            'is_active': True,
        }
    )
    produtos[prod_data['sku']] = produto
    if created:
        print(f"✓ Produto criado: {produto.name}")

# Criar algumas movimentações de exemplo
movimentacoes_data = [
    {
        'product_sku': 'ALM001',
        'type': 'ENTRADA',
        'quantity': 50,
        'document': 'NF-001234',
        'notes': 'Compra inicial - fornecedor ABC',
    },
    {
        'product_sku': 'ALM001',
        'type': 'SAIDA',
        'quantity': 25,
        'document': 'VD-000123',
        'notes': 'Venda para cliente XYZ',
    },
    {
        'product_sku': 'BEB002',
        'type': 'ENTRADA',
        'quantity': 200,
        'document': 'NF-001235',
        'notes': 'Reposição de estoque',
    },
    {
        'product_sku': 'BEB002',
        'type': 'SAIDA',
        'quantity': 80,
        'document': 'VD-000124',
        'notes': 'Venda atacado',
    },
    {
        'product_sku': 'HIG001',
        'type': 'ENTRADA',
        'quantity': 20,
        'document': 'NF-001236',
        'notes': 'Nova linha de produtos',
    },
    {
        'product_sku': 'HIG001',
        'type': 'SAIDA',
        'quantity': 12,
        'document': 'VD-000125',
        'notes': 'Vendas diversas',
    },
]

print("\n--- Criando movimentações ---")
for mov_data in movimentacoes_data:
    try:
        # Reset estoque para 0 antes de criar movimentações
        produto = produtos[mov_data['product_sku']]
        
        movimento = InventoryMovement.objects.create(
            product=produto,
            type=mov_data['type'],
            quantity=Decimal(str(mov_data['quantity'])),
            document=mov_data['document'],
            notes=mov_data['notes'],
            user=admin_user,
        )
        print(f"✓ Movimentação criada: {movimento}")
    except Exception as e:
        print(f"✗ Erro ao criar movimentação {mov_data}: {e}")

print("\n🎉 Dados de exemplo criados com sucesso!")
print(f"📊 Total de produtos: {Product.objects.count()}")
print(f"📦 Total de movimentações: {InventoryMovement.objects.count()}")
print("\n🔑 Acesso ao sistema:")
print("   Usuário: admin")
print("   Senha: admin123")
print("\n🌐 Para iniciar o servidor: python manage.py runserver")