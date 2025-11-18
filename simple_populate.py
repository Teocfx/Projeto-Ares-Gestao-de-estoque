"""
Script simplificado para criar dados de exemplo
"""
from produtos.models import Category, Unit, Product
from movimentacoes.models import InventoryMovement
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

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

print("✓ Usuário admin verificado")

# Criar categorias
alimentos, _ = Category.objects.get_or_create(name='Alimentos', defaults={'description': 'Produtos alimentícios'})
bebidas, _ = Category.objects.get_or_create(name='Bebidas', defaults={'description': 'Bebidas diversas'})
higiene, _ = Category.objects.get_or_create(name='Higiene', defaults={'description': 'Produtos de higiene'})

print("✓ Categorias criadas")

# Criar unidades
un, _ = Unit.objects.get_or_create(name='UN', defaults={'description': 'Unidade'})
kg, _ = Unit.objects.get_or_create(name='KG', defaults={'description': 'Quilograma'})
l, _ = Unit.objects.get_or_create(name='L', defaults={'description': 'Litro'})

print("✓ Unidades criadas")

# Criar produtos
arroz, created = Product.objects.get_or_create(
    sku='ALM001',
    defaults={
        'name': 'Arroz Integral 1kg',
        'description': 'Arroz integral tipo 1',
        'category': alimentos,
        'unit': un,
        'min_stock': Decimal('10'),
        'current_stock': Decimal('25'),
        'unit_price': Decimal('8.90'),
        'expiry_date': date.today() + timedelta(days=180),
    }
)

feijao, created = Product.objects.get_or_create(
    sku='ALM002',
    defaults={
        'name': 'Feijão Carioca 1kg',
        'description': 'Feijão carioca tipo 1',
        'category': alimentos,
        'unit': un,
        'min_stock': Decimal('8'),
        'current_stock': Decimal('3'),  # Estoque baixo
        'unit_price': Decimal('6.90'),
        'expiry_date': date.today() + timedelta(days=365),
    }
)

refrigerante, created = Product.objects.get_or_create(
    sku='BEB001',
    defaults={
        'name': 'Refrigerante Cola 2L',
        'description': 'Refrigerante sabor cola',
        'category': bebidas,
        'unit': un,
        'min_stock': Decimal('15'),
        'current_stock': Decimal('0'),  # Estoque zerado
        'unit_price': Decimal('5.99'),
        'expiry_date': date.today() + timedelta(days=90),
    }
)

agua, created = Product.objects.get_or_create(
    sku='BEB002',
    defaults={
        'name': 'Água Mineral 500ml',
        'description': 'Água mineral natural',
        'category': bebidas,
        'unit': un,
        'min_stock': Decimal('50'),
        'current_stock': Decimal('120'),
        'unit_price': Decimal('2.50'),
        'expiry_date': date.today() + timedelta(days=730),
    }
)

shampoo, created = Product.objects.get_or_create(
    sku='HIG001',
    defaults={
        'name': 'Shampoo Anticaspa 400ml',
        'description': 'Shampoo anticaspa uso diário',
        'category': higiene,
        'unit': un,
        'min_stock': Decimal('5'),
        'current_stock': Decimal('8'),
        'unit_price': Decimal('18.90'),
        'expiry_date': date.today() + timedelta(days=1095),
    }
)

print("✓ Produtos criados")

# Criar algumas movimentações (apenas se não existirem)
if InventoryMovement.objects.count() == 0:
    # Movimentação de entrada para arroz
    InventoryMovement.objects.create(
        product=arroz,
        type='ENTRADA',
        quantity=Decimal('50'),
        document='NF-001234',
        notes='Compra inicial',
        user=admin_user,
    )
    
    # Movimentação de saída para arroz
    arroz.refresh_from_db()
    InventoryMovement.objects.create(
        product=arroz,
        type='SAIDA',
        quantity=Decimal('25'),
        document='VD-000123',
        notes='Venda cliente XYZ',
        user=admin_user,
    )
    
    # Movimentação de entrada para água
    InventoryMovement.objects.create(
        product=agua,
        type='ENTRADA',
        quantity=Decimal('200'),
        document='NF-001235',
        notes='Reposição estoque',
        user=admin_user,
    )
    
    # Movimentação de saída para água
    agua.refresh_from_db()
    InventoryMovement.objects.create(
        product=agua,
        type='SAIDA',
        quantity=Decimal('80'),
        document='VD-000124',
        notes='Venda atacado',
        user=admin_user,
    )
    
    print("✓ Movimentações criadas")

print("\n🎉 Dados de exemplo criados com sucesso!")
print(f"📊 Total de produtos: {Product.objects.count()}")
print(f"📦 Total de movimentações: {InventoryMovement.objects.count()}")
print("\n🔑 Acesso ao sistema:")
print("   Usuário: admin")
print("   Senha: admin123")
print("\n🌐 Para iniciar o servidor: python manage.py runserver")