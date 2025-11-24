"""
Script expandido para gerar um banco COMPLETO de testes
para seu sistema de estoque.
Gera:
- Usuário admin
- Categorias
- Unidades
- 30 produtos variados
- Movimentações distribuídas durante o ano todo
"""

from produtos.models import Category, Unit, Product
from movimentacoes.models import InventoryMovement
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
import random

User = get_user_model()

# Criar usuário admin
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()

print("✓ Usuário admin verificado")

# Criar Categorias
category_names = [
    "Alimentos", "Bebidas", "Higiene", "Limpeza", "Ferramentas",
    "Eletrônicos", "Estacionário", "Medicamentos", "Vestuário",
    "Cozinha", "Automotivo", "Jardinagem"
]

categories = {}

for name in category_names:
    cat, _ = Category.objects.get_or_create(name=name, defaults={'description': f'Categoria de {name}'})
    categories[name] = cat

print(f"✓ {len(categories)} categorias criadas")

# Criar Unidades
unit_data = {
    "UN": "Unidade",
    "CX": "Caixa",
    "KG": "Quilograma",
    "G": "Gramas",
    "L": "Litro",
    "ML": "Mililitro",
    "PC": "Pacote",
    "MT": "Metro"
}

units = {}

for abbr, desc in unit_data.items():
    unit, _ = Unit.objects.get_or_create(name=abbr, defaults={'description': desc})
    units[abbr] = unit

print(f"✓ {len(units)} unidades criadas")


# Criar produtos
product_templates = [
    ("Arroz Integral 1kg", "ALM001", "Alimentos", "KG", 8.90),
    ("Feijão Carioca 1kg", "ALM002", "Alimentos", "KG", 6.90),
    ("Açúcar Refinado 1kg", "ALM003", "Alimentos", "KG", 4.50),
    ("Macarrão Espaguete 500g", "ALM004", "Alimentos", "G", 3.40),
    ("Café Torrado 500g", "ALM005", "Alimentos", "G", 12.90),
    
    ("Refrigerante Cola 2L", "BEB001", "Bebidas", "L", 6.90),
    ("Suco de Laranja 1L", "BEB002", "Bebidas", "L", 5.00),
    ("Água Mineral 500ml", "BEB003", "Bebidas", "ML", 2.00),
    
    ("Shampoo Anticaspa", "HIG001", "Higiene", "ML", 15.90),
    ("Sabonete Neutro", "HIG002", "Higiene", "UN", 2.50),
    ("Pasta de Dente", "HIG003", "Higiene", "UN", 4.90),
    
    ("Detergente Neutro", "LIM001", "Limpeza", "ML", 3.20),
    ("Água Sanitária 2L", "LIM002", "Limpeza", "L", 4.50),
    
    ("Martelo de Aço", "FER001", "Ferramentas", "UN", 25.90),
    ("Chave de Fenda", "FER002", "Ferramentas", "UN", 9.90),
    
    ("Mouse USB", "ELT001", "Eletrônicos", "UN", 35.90),
    ("Teclado Mecânico", "ELT002", "Eletrônicos", "UN", 199.90),
    
    ("Caderno 100 folhas", "ESC001", "Estacionário", "UN", 7.40),
    ("Caneta Azul", "ESC002", "Estacionário", "UN", 1.70),
    
    ("Dipirona 500mg", "MED001", "Medicamentos", "PC", 12.00),
    ("Paracetamol 750mg", "MED002", "Medicamentos", "PC", 10.00),
    
    ("Camiseta Branca M", "VST001", "Vestuário", "UN", 19.90),
    ("Calça Jeans 42", "VST002", "Vestuário", "UN", 69.90),

    ("Frigideira Antiaderente", "COZ001", "Cozinha", "UN", 45.00),
    ("Panela de Pressão 4L", "COZ002", "Cozinha", "UN", 89.90),

    ("Óleo 20W50", "AUT001", "Automotivo", "L", 24.90),
    ("Lâmpada Automotiva H7", "AUT002", "Automotivo", "UN", 14.90),

    ("Sementes de Tomate", "JAR001", "Jardinagem", "G", 3.90),
    ("Adubo Orgânico 5kg", "JAR002", "Jardinagem", "KG", 19.90)
]

products = []

for name, sku, cat, unit, price in product_templates:
    prod, _ = Product.objects.get_or_create(
        sku=sku,
        defaults={
            'name': name,
            'description': name,
            'category': categories[cat],
            'unit': units[unit],
            'min_stock': Decimal(random.randint(5, 20)),
            'current_stock': Decimal(random.randint(0, 200)),
            'unit_price': Decimal(price),
            'expiry_date': date.today() + timedelta(days=random.randint(90, 1095)),
        }
    )
    products.append(prod)

print(f"✓ {len(products)} produtos criados")

# Criar MOVIMENTAÇÕES automáticas
movement_types = ["ENTRADA", "SAIDA", "AJUSTE", "INVENTARIO"]

if InventoryMovement.objects.count() < 50:
    print("⏳ Gerando movimentações...")

    for prod in products:
        for _ in range(random.randint(5, 15)):  # 5–15 movimentações por produto
            days_ago = random.randint(1, 365)
            movement_date = date.today() - timedelta(days=days_ago)

            InventoryMovement.objects.create(
                product=prod,
                type=random.choice(movement_types),
                quantity=Decimal(random.randint(1, 50)),
                document=f"DOC-{random.randint(1000, 9999)}",
                notes="Movimentação automática para testes",
                user=admin_user,
                created_at=movement_date
            )

    print("✓ Movimentações geradas")

print("\n🎉 BANCO DE TESTES CRIADO COM SUCESSO!")
print(f"📦 Total de produtos: {Product.objects.count()}")
print(f"📊 Total de movimentações: {InventoryMovement.objects.count()}")
print("\n🔑 Login:")
print("   Usuário: admin")
print("   Senha: admin123")
