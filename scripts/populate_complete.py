#!/usr/bin/env python3
"""
Script COMPLETO para popular banco de dados com dados realistas de teste.
Gera dados de 5 anos (2020-2025) para testar gráficos e relatórios.

Uso: python3 manage.py shell < scripts/populate_complete.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitepadrao.settings.development')
django.setup()

from produtos.models import Category, Unit, Product
from movimentacoes.models import InventoryMovement
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models

User = get_user_model()

print("=" * 70)
print("🚀 SCRIPT DE POPULAÇÃO COMPLETA DO BANCO DE DADOS")
print("=" * 70)
print("📅 Período: 2020-2025 (5 anos de histórico)")
print("📦 Dados: Categorias, Unidades, Produtos, Movimentações")
print("=" * 70)

# ============================================================================
# USUÁRIOS
# ============================================================================
print("\n👥 Criando usuários...")

admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@example.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✓ Usuário admin criado")
else:
    print("✓ Usuário admin já existe")

# Criar usuários operacionais
usuarios_operacionais = [
    ('joao.silva', 'João Silva', 'joao@example.com'),
    ('maria.santos', 'Maria Santos', 'maria@example.com'),
    ('carlos.oliveira', 'Carlos Oliveira', 'carlos@example.com'),
]

usuarios = [admin_user]
for username, nome_completo, email in usuarios_operacionais:
    nome, sobrenome = nome_completo.split(' ', 1)
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': nome,
            'last_name': sobrenome,
            'is_staff': False,
        }
    )
    if created:
        user.set_password('senha123')
        user.save()
        print(f"✓ Usuário {username} criado")
    usuarios.append(user)

# ============================================================================
# CATEGORIAS
# ============================================================================
print("\n🏷️ Criando categorias...")

categorias_data = [
    {'name': 'Alimentos', 'description': 'Produtos alimentícios em geral'},
    {'name': 'Bebidas', 'description': 'Bebidas alcoólicas e não-alcoólicas'},
    {'name': 'Higiene', 'description': 'Produtos de higiene pessoal'},
    {'name': 'Limpeza', 'description': 'Produtos de limpeza doméstica'},
    {'name': 'Eletrônicos', 'description': 'Aparelhos e equipamentos eletrônicos'},
    {'name': 'Papelaria', 'description': 'Material de escritório e papelaria'},
    {'name': 'Ferramentas', 'description': 'Ferramentas e equipamentos'},
    {'name': 'Vestuário', 'description': 'Roupas e acessórios'},
    {'name': 'Automotivo', 'description': 'Peças e acessórios automotivos'},
    {'name': 'Jardinagem', 'description': 'Produtos para jardinagem'},
    {'name': 'Pet Shop', 'description': 'Produtos para animais de estimação'},
    {'name': 'Medicamentos', 'description': 'Medicamentos e suplementos'},
]

categorias = {}
for cat_data in categorias_data:
    categoria, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categorias[cat_data['name']] = categoria
    if created:
        print(f"✓ Categoria: {categoria.name}")

# ============================================================================
# UNIDADES
# ============================================================================
print("\n📏 Criando unidades de medida...")

unidades_data = [
    {'name': 'UN', 'description': 'Unidade'},
    {'name': 'KG', 'description': 'Quilograma'},
    {'name': 'G', 'description': 'Gramas'},
    {'name': 'L', 'description': 'Litro'},
    {'name': 'ML', 'description': 'Mililitro'},
    {'name': 'CX', 'description': 'Caixa'},
    {'name': 'PC', 'description': 'Pacote'},
    {'name': 'MT', 'description': 'Metro'},
    {'name': 'CM', 'description': 'Centímetro'},
    {'name': 'DZ', 'description': 'Dúzia'},
]

unidades = {}
for unit_data in unidades_data:
    unidade, created = Unit.objects.get_or_create(
        name=unit_data['name'],
        defaults={'description': unit_data['description']}
    )
    unidades[unit_data['name']] = unidade
    if created:
        print(f"✓ Unidade: {unidade.name}")

# ============================================================================
# PRODUTOS (50+ produtos variados)
# ============================================================================
print("\n📦 Criando produtos...")

produtos_data = [
    # Alimentos (15 produtos)
    ("Arroz Integral 1kg", "ALM001", "Alimentos", "KG", 8.90, 180),
    ("Feijão Carioca 1kg", "ALM002", "Alimentos", "KG", 6.90, 365),
    ("Açúcar Refinado 1kg", "ALM003", "Alimentos", "KG", 4.50, 730),
    ("Macarrão Espaguete 500g", "ALM004", "Alimentos", "G", 3.40, 365),
    ("Café Torrado 500g", "ALM005", "Alimentos", "G", 12.90, 180),
    ("Óleo de Soja 900ml", "ALM006", "Alimentos", "ML", 7.90, 365),
    ("Sal Refinado 1kg", "ALM007", "Alimentos", "KG", 2.50, 1460),
    ("Farinha de Trigo 1kg", "ALM008", "Alimentos", "KG", 5.90, 180),
    ("Leite UHT Integral 1L", "ALM009", "Alimentos", "L", 5.90, 120),
    ("Chocolate ao Leite 200g", "ALM010", "Alimentos", "G", 8.90, 365),
    ("Biscoito Cream Cracker", "ALM011", "Alimentos", "PC", 3.90, 180),
    ("Molho de Tomate 340g", "ALM012", "Alimentos", "G", 4.50, 730),
    ("Sardinha em Lata 125g", "ALM013", "Alimentos", "G", 6.90, 1095),
    ("Extrato de Tomate 130g", "ALM014", "Alimentos", "G", 2.90, 730),
    ("Maionese 500g", "ALM015", "Alimentos", "G", 8.90, 180),
    
    # Bebidas (10 produtos)
    ("Refrigerante Cola 2L", "BEB001", "Bebidas", "L", 6.90, 180),
    ("Água Mineral 500ml", "BEB002", "Bebidas", "ML", 2.00, 730),
    ("Suco de Laranja 1L", "BEB003", "Bebidas", "L", 5.90, 30),
    ("Cerveja Lata 350ml", "BEB004", "Bebidas", "ML", 3.90, 365),
    ("Energético 250ml", "BEB005", "Bebidas", "ML", 7.90, 365),
    ("Chá Gelado 1.5L", "BEB006", "Bebidas", "L", 4.90, 180),
    ("Água de Coco 1L", "BEB007", "Bebidas", "L", 8.90, 180),
    ("Refrigerante Guaraná 2L", "BEB008", "Bebidas", "L", 6.50, 180),
    ("Suco de Uva Integral 1L", "BEB009", "Bebidas", "L", 12.90, 365),
    ("Isotônico 500ml", "BEB010", "Bebidas", "ML", 4.50, 365),
    
    # Higiene (10 produtos)
    ("Shampoo Anticaspa 400ml", "HIG001", "Higiene", "ML", 18.90, 1095),
    ("Condicionador 400ml", "HIG002", "Higiene", "ML", 16.90, 1095),
    ("Sabonete Líquido 250ml", "HIG003", "Higiene", "ML", 8.90, 730),
    ("Creme Dental 90g", "HIG004", "Higiene", "G", 4.50, 730),
    ("Desodorante Roll-on 50ml", "HIG005", "Higiene", "ML", 12.90, 730),
    ("Papel Higiênico 12 rolos", "HIG006", "Higiene", "PC", 22.90, None),
    ("Absorvente Pacote 8un", "HIG007", "Higiene", "PC", 8.90, 1095),
    ("Fio Dental 50m", "HIG008", "Higiene", "MT", 6.90, 730),
    ("Enxaguante Bucal 500ml", "HIG009", "Higiene", "ML", 14.90, 730),
    ("Sabonete Barra 90g", "HIG010", "Higiene", "G", 2.50, 730),
    
    # Limpeza (8 produtos)
    ("Detergente Neutro 500ml", "LIM001", "Limpeza", "ML", 3.20, 1460),
    ("Água Sanitária 2L", "LIM002", "Limpeza", "L", 4.50, 730),
    ("Desinfetante 2L", "LIM003", "Limpeza", "L", 7.90, 730),
    ("Sabão em Pó 1kg", "LIM004", "Limpeza", "KG", 12.90, 730),
    ("Amaciante 2L", "LIM005", "Limpeza", "L", 9.90, 730),
    ("Esponja de Limpeza Pacote", "LIM006", "Limpeza", "PC", 5.90, None),
    ("Pano de Chão", "LIM007", "Limpeza", "UN", 8.90, None),
    ("Lustra Móveis 200ml", "LIM008", "Limpeza", "ML", 11.90, 730),
    
    # Eletrônicos (8 produtos)
    ("Carregador USB-C 25W", "ELE001", "Eletrônicos", "UN", 39.90, None),
    ("Cabo HDMI 2m", "ELE002", "Eletrônicos", "UN", 29.90, None),
    ("Mouse Wireless", "ELE003", "Eletrônicos", "UN", 45.90, None),
    ("Teclado USB", "ELE004", "Eletrônicos", "UN", 59.90, None),
    ("Pendrive 32GB", "ELE005", "Eletrônicos", "UN", 35.90, None),
    ("Fone de Ouvido Bluetooth", "ELE006", "Eletrônicos", "UN", 89.90, None),
    ("Carregador Portátil 10000mAh", "ELE007", "Eletrônicos", "UN", 79.90, None),
    ("Adaptador HDMI-VGA", "ELE008", "Eletrônicos", "UN", 24.90, None),
    
    # Papelaria (8 produtos)
    ("Caderno 100 folhas", "PAP001", "Papelaria", "UN", 12.90, None),
    ("Caneta Azul Caixa 50un", "PAP002", "Papelaria", "CX", 45.90, None),
    ("Lápis HB Caixa 72un", "PAP003", "Papelaria", "CX", 38.90, None),
    ("Borracha Branca", "PAP004", "Papelaria", "UN", 1.50, None),
    ("Papel A4 Resma 500fls", "PAP005", "Papelaria", "PC", 29.90, None),
    ("Grampeador Médio", "PAP006", "Papelaria", "UN", 18.90, None),
    ("Tesoura 21cm", "PAP007", "Papelaria", "UN", 12.90, None),
    ("Cola Bastão 40g", "PAP008", "Papelaria", "G", 4.90, None),
    
    # Ferramentas (6 produtos)
    ("Martelo de Aço 500g", "FER001", "Ferramentas", "UN", 25.90, None),
    ("Chave de Fenda Jogo 6pç", "FER002", "Ferramentas", "UN", 34.90, None),
    ("Alicate Universal 8pol", "FER003", "Ferramentas", "UN", 28.90, None),
    ("Trena 5 metros", "FER004", "Ferramentas", "UN", 19.90, None),
    ("Furadeira Elétrica", "FER005", "Ferramentas", "UN", 189.90, None),
    ("Jogo de Brocas 13pç", "FER006", "Ferramentas", "UN", 45.90, None),
    
    # Vestuário (5 produtos)
    ("Camiseta Branca M", "VST001", "Vestuário", "UN", 29.90, None),
    ("Calça Jeans 42", "VST002", "Vestuário", "UN", 89.90, None),
    ("Meia Soquete Kit 3pares", "VST003", "Vestuário", "PC", 19.90, None),
    ("Bermuda Tactel G", "VST004", "Vestuário", "UN", 49.90, None),
    ("Boné Ajustável", "VST005", "Vestuário", "UN", 35.90, None),
    
    # Automotivo (5 produtos)
    ("Óleo Motor 20W50 1L", "AUT001", "Automotivo", "L", 32.90, None),
    ("Lâmpada H7 12V", "AUT002", "Automotivo", "UN", 18.90, None),
    ("Filtro de Óleo", "AUT003", "Automotivo", "UN", 24.90, None),
    ("Palheta Limpador 18pol", "AUT004", "Automotivo", "UN", 29.90, None),
    ("Aditivo Radiador 1L", "AUT005", "Automotivo", "L", 19.90, None),
    
    # Jardinagem (4 produtos)
    ("Semente Tomate 10g", "JAR001", "Jardinagem", "G", 5.90, 365),
    ("Adubo Orgânico 5kg", "JAR002", "Jardinagem", "KG", 24.90, None),
    ("Mangueira Jardim 30m", "JAR003", "Jardinagem", "MT", 89.90, None),
    ("Pá de Jardim", "JAR004", "Jardinagem", "UN", 22.90, None),
    
    # Pet Shop (4 produtos)
    ("Ração Cães Adultos 15kg", "PET001", "Pet Shop", "KG", 129.90, 365),
    ("Ração Gatos Adultos 10kg", "PET002", "Pet Shop", "KG", 159.90, 365),
    ("Areia Higiênica Gatos 4kg", "PET003", "Pet Shop", "KG", 24.90, None),
    ("Brinquedo Corda Cães", "PET004", "Pet Shop", "UN", 15.90, None),
    
    # Medicamentos (5 produtos)
    ("Dipirona 500mg 20cp", "MED001", "Medicamentos", "CX", 8.90, 730),
    ("Paracetamol 750mg 20cp", "MED002", "Medicamentos", "CX", 12.90, 730),
    ("Vitamina C 1g 30cp", "MED003", "Medicamentos", "CX", 29.90, 730),
    ("Soro Fisiológico 500ml", "MED004", "Medicamentos", "ML", 6.90, 730),
    ("Curativo Adesivo Pacote", "MED005", "Medicamentos", "PC", 8.90, 1095),
]

produtos = []
for name, sku, cat_name, unit_name, price, expiry_days in produtos_data:
    # Calcular validade
    expiry = None
    if expiry_days:
        expiry = date.today() + timedelta(days=expiry_days)
    
    # Estoque inicial aleatório
    initial_stock = Decimal(random.randint(0, 200))
    min_stock = Decimal(random.randint(5, 30))
    
    produto, created = Product.objects.get_or_create(
        sku=sku,
        defaults={
            'name': name,
            'description': f"{name} - Produto de qualidade",
            'category': categorias[cat_name],
            'unit': unidades[unit_name],
            'min_stock': min_stock,
            'current_stock': initial_stock,
            'unit_price': Decimal(str(price)),
            'expiry_date': expiry,
            'is_active': True,
        }
    )
    
    if created:
        # Resetar estoque para 0 antes de criar movimentações
        produto.current_stock = Decimal('0')
        produto.save()
        print(f"✓ Produto: {produto.name}")
    
    produtos.append(produto)

# ============================================================================
# MOVIMENTAÇÕES (Últimos 5 anos - 2020 a 2025)
# ============================================================================
print(f"\n📊 Criando movimentações (2020-2025)...")
print("⏳ Isso pode levar alguns minutos...")

# Data inicial: 01/01/2020
data_inicial = datetime(2020, 1, 1)
data_final = datetime.now()
total_dias = (data_final - data_inicial).days

# Tipos e suas probabilidades
tipos_movimentacao = [
    (InventoryMovement.ENTRADA, 45),   # 45% entradas
    (InventoryMovement.SAIDA, 45),     # 45% saídas
    (InventoryMovement.AJUSTE, 10),    # 10% ajustes
]

# Prefixos de documento
prefixos_doc = {
    InventoryMovement.ENTRADA: ["NF", "NFe", "TRF-E"],
    InventoryMovement.SAIDA: ["VD", "SAI", "TRF-S"],
    InventoryMovement.AJUSTE: ["AJ", "CORR", "INV"],
}

# Notas por tipo
notas_por_tipo = {
    InventoryMovement.ENTRADA: [
        "Compra de fornecedor",
        "Reposição de estoque",
        "Entrada por transferência",
        "Devolução de cliente",
        "Bonificação",
    ],
    InventoryMovement.SAIDA: [
        "Venda para cliente",
        "Baixa por consumo",
        "Transferência",
        "Amostra grátis",
        "Perda por validade",
    ],
    InventoryMovement.AJUSTE: [
        "Ajuste de inventário",
        "Correção de estoque",
        "Quebra identificada",
        "Diferença de contagem",
        "Inventário físico",
        "Contagem periódica",
    ],
}

# Gerar aproximadamente 10-20 movimentações por produto ao longo de 5 anos
movimentacoes_criadas = 0
movimentacoes_erro = 0

for produto in produtos:
    num_movimentacoes = random.randint(15, 30)  # 15-30 movimentações por produto
    
    for _ in range(num_movimentacoes):
        try:
            # Data aleatória entre 2020 e hoje
            dias_aleatorios = random.randint(0, total_dias)
            data_mov = data_inicial + timedelta(
                days=dias_aleatorios,
                hours=random.randint(8, 18),  # Horário comercial
                minutes=random.randint(0, 59)
            )
            
            # Escolher tipo de movimentação
            tipo = random.choices(
                [t[0] for t in tipos_movimentacao],
                weights=[t[1] for t in tipos_movimentacao],
                k=1
            )[0]
            
            # Definir quantidade baseada no tipo
            if tipo == InventoryMovement.ENTRADA:
                quantidade = Decimal(random.uniform(10, 100))
            
            elif tipo == InventoryMovement.SAIDA:
                # Não pode vender mais do que tem
                if produto.current_stock <= 0:
                    continue
                max_venda = min(float(produto.current_stock), 50)
                quantidade = Decimal(random.uniform(1, max_venda))
            
            elif tipo == InventoryMovement.AJUSTE:
                # 60% ajustes negativos, 40% positivos
                if random.random() < 0.6:
                    # Ajuste negativo (quebra, perda, inventário com diferença negativa)
                    quantidade = Decimal(random.uniform(0.5, 10))
                else:
                    # Ajuste positivo (inventário com diferença positiva, correção)
                    quantidade = Decimal(random.uniform(0.5, 15))
            
            # Arredondar para 2 casas decimais
            quantidade = quantidade.quantize(Decimal('0.01'))
            
            # Documento (85% possuem)
            documento = ""
            if random.random() < 0.85:
                prefixo = random.choice(prefixos_doc[tipo])
                numero = random.randint(100000, 999999)
                documento = f"{prefixo}-{numero}"
            
            # Notas (75% possuem)
            notas = ""
            if random.random() < 0.75:
                notas = random.choice(notas_por_tipo[tipo])
            
            # Usuário aleatório
            usuario = random.choice(usuarios)
            
            # Criar movimentação SEM salvar ainda
            movimento = InventoryMovement(
                product=produto,
                type=tipo,
                quantity=quantidade,
                document=documento,
                notes=notas,
                user=usuario,
            )
            
            # Salvar uma primeira vez (isso vai atualizar o estoque)
            movimento.save()
            
            # Agora atualizar a data usando update (bypass do auto_now_add)
            InventoryMovement.objects.filter(pk=movimento.pk).update(created_at=data_mov)
            
            movimentacoes_criadas += 1
            
            # Progress indicator
            if movimentacoes_criadas % 100 == 0:
                print(f"  ✓ {movimentacoes_criadas} movimentações criadas...")
        
        except Exception as e:
            movimentacoes_erro += 1
            continue

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("\n" + "=" * 70)
print("🎉 POPULAÇÃO CONCLUÍDA COM SUCESSO!")
print("=" * 70)

# Estatísticas de produtos
total_produtos = Product.objects.count()
produtos_ativos = Product.objects.filter(is_active=True).count()
criticos = Product.objects.filter(current_stock=0).count()
baixos = Product.objects.filter(
    current_stock__gt=0,
    current_stock__lte=models.F('min_stock')
).count()

print(f"\n📦 PRODUTOS:")
print(f"   Total: {total_produtos}")
print(f"   Ativos: {produtos_ativos}")
print(f"   🔴 Críticos (estoque 0): {criticos}")
print(f"   🟡 Baixos: {baixos}")

# Estatísticas de movimentações
total_mov = InventoryMovement.objects.count()
entradas = InventoryMovement.objects.filter(type=InventoryMovement.ENTRADA).count()
saidas = InventoryMovement.objects.filter(type=InventoryMovement.SAIDA).count()
ajustes = InventoryMovement.objects.filter(type=InventoryMovement.AJUSTE).count()

print(f"\n📊 MOVIMENTAÇÕES:")
print(f"   Total: {total_mov}")
print(f"   ⬇️  Entradas: {entradas} ({entradas*100//total_mov if total_mov else 0}%)")
print(f"   ⬆️  Saídas: {saidas} ({saidas*100//total_mov if total_mov else 0}%)")
print(f"   🔄 Ajustes: {ajustes} ({ajustes*100//total_mov if total_mov else 0}%)")

if movimentacoes_erro > 0:
    print(f"   ⚠️  Erros: {movimentacoes_erro}")

# Estatísticas por categoria
print(f"\n🏷️ CATEGORIAS:")
from django.db.models import Count, Sum
for categoria in Category.objects.all():
    qtd_produtos = categoria.products.count()
    total_estoque = categoria.products.aggregate(
        total=Sum('current_stock')
    )['total'] or 0
    print(f"   {categoria.name}: {qtd_produtos} produtos, estoque: {total_estoque:.2f}")

# Informações de acesso
print(f"\n🔑 ACESSO AO SISTEMA:")
print(f"   URL: http://localhost:8000")
print(f"   Usuário: admin")
print(f"   Senha: admin123")
print(f"\n   Operadores:")
for username, nome, _ in usuarios_operacionais:
    print(f"   - {username} / senha123 ({nome})")

print("\n" + "=" * 70)
print("✅ Script finalizado! Banco de dados pronto para uso.")
print("=" * 70)
