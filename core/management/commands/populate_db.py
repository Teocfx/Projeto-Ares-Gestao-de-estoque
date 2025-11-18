"""
Comando para popular o banco de dados com dados de exemplo.
Uso: python manage.py populate_db
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from produtos.models import Category, Unit, Product
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o banco de dados com dados de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo se já existirem dados',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando população do banco de dados...')
        )
        
        # Criar usuário admin
        self.create_admin_user()
        
        # Criar dados básicos apenas se não existirem ou se forçado
        if not Product.objects.exists() or options['force']:
            self.create_categories()
            self.create_units() 
            self.create_products()
            
            self.stdout.write(
                self.style.SUCCESS('🎉 Banco de dados populado com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING('⚠️ Dados já existem. Use --force para sobrescrever.')
            )
            
        self.show_summary()

    def create_admin_user(self):
        """Criar usuário administrador."""
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
            self.stdout.write('✓ Usuário admin criado')
        else:
            self.stdout.write('✓ Usuário admin já existe')

    def create_categories(self):
        """Criar categorias de produtos."""
        categories_data = [
            {'name': 'Alimentos', 'description': 'Produtos alimentícios em geral'},
            {'name': 'Bebidas', 'description': 'Bebidas alcoólicas e não-alcoólicas'},
            {'name': 'Higiene', 'description': 'Produtos de higiene pessoal'},
            {'name': 'Limpeza', 'description': 'Produtos de limpeza doméstica'},
            {'name': 'Eletrônicos', 'description': 'Aparelhos e equipamentos eletrônicos'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'✓ Categoria criada: {category.name}')

    def create_units(self):
        """Criar unidades de medida."""
        units_data = [
            {'name': 'UN', 'description': 'Unidade'},
            {'name': 'KG', 'description': 'Quilograma'},
            {'name': 'L', 'description': 'Litro'},
            {'name': 'ML', 'description': 'Mililitro'},
            {'name': 'CX', 'description': 'Caixa'},
            {'name': 'PC', 'description': 'Peça'},
        ]
        
        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                name=unit_data['name'],
                defaults={'description': unit_data['description']}
            )
            if created:
                self.stdout.write(f'✓ Unidade criada: {unit.name}')

    def create_products(self):
        """Criar produtos de exemplo."""
        # Obter categorias e unidades
        alimentos = Category.objects.get(name='Alimentos')
        bebidas = Category.objects.get(name='Bebidas')
        higiene = Category.objects.get(name='Higiene')
        limpeza = Category.objects.get(name='Limpeza')
        eletronicos = Category.objects.get(name='Eletrônicos')
        
        un = Unit.objects.get(name='UN')
        # kg e l não são usados diretamente, mas mantidos no banco
        
        products_data = [
            {
                'sku': 'ALM001',
                'name': 'Arroz Integral 1kg',
                'description': 'Arroz integral tipo 1, embalagem 1kg',
                'category': alimentos,
                'unit': un,
                'min_stock': Decimal('10'),
                'current_stock': Decimal('25'),
                'unit_price': Decimal('8.90'),
                'expiry_date': date.today() + timedelta(days=180),
            },
            {
                'sku': 'ALM002',
                'name': 'Feijão Carioca 1kg',
                'description': 'Feijão carioca tipo 1, embalagem 1kg',
                'category': alimentos,
                'unit': un,
                'min_stock': Decimal('8'),
                'current_stock': Decimal('3'),  # Estoque baixo
                'unit_price': Decimal('6.90'),
                'expiry_date': date.today() + timedelta(days=365),
            },
            {
                'sku': 'BEB001',
                'name': 'Refrigerante Cola 2L',
                'description': 'Refrigerante sabor cola, garrafa 2 litros',
                'category': bebidas,
                'unit': un,
                'min_stock': Decimal('15'),
                'current_stock': Decimal('0'),  # Estoque crítico
                'unit_price': Decimal('5.99'),
                'expiry_date': date.today() + timedelta(days=90),
            },
            {
                'sku': 'BEB002',
                'name': 'Água Mineral 500ml',
                'description': 'Água mineral natural, garrafa 500ml',
                'category': bebidas,
                'unit': un,
                'min_stock': Decimal('50'),
                'current_stock': Decimal('120'),
                'unit_price': Decimal('2.50'),
                'expiry_date': date.today() + timedelta(days=730),
            },
            {
                'sku': 'HIG001',
                'name': 'Shampoo Anticaspa 400ml',
                'description': 'Shampoo anticaspa para uso diário',
                'category': higiene,
                'unit': un,
                'min_stock': Decimal('5'),
                'current_stock': Decimal('8'),
                'unit_price': Decimal('18.90'),
                'expiry_date': date.today() + timedelta(days=1095),
            },
            {
                'sku': 'LIM001',
                'name': 'Detergente Neutro 500ml',
                'description': 'Detergente neutro para louças',
                'category': limpeza,
                'unit': un,
                'min_stock': Decimal('12'),
                'current_stock': Decimal('45'),
                'unit_price': Decimal('4.50'),
                'expiry_date': date.today() + timedelta(days=1460),
            },
            {
                'sku': 'ELE001',
                'name': 'Carregador USB-C',
                'description': 'Carregador rápido USB-C 25W',
                'category': eletronicos,
                'unit': un,
                'min_stock': Decimal('3'),
                'current_stock': Decimal('12'),
                'unit_price': Decimal('39.90'),
                'expiry_date': None,  # Sem vencimento
            },
            {
                'sku': 'ALM003',
                'name': 'Leite UHT Integral 1L',
                'description': 'Leite UHT integral, embalagem longa vida',
                'category': alimentos,
                'unit': un,
                'min_stock': Decimal('20'),
                'current_stock': Decimal('15'),  # Estoque baixo
                'unit_price': Decimal('5.90'),
                'expiry_date': date.today() + timedelta(days=30),  # Vence em breve
            },
        ]
        
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=prod_data['sku'],
                defaults=prod_data
            )
            if created:
                self.stdout.write(f'✓ Produto criado: {product.name}')

    def show_summary(self):
        """Mostrar resumo dos dados criados."""
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMO DO SISTEMA')
        self.stdout.write('='*50)
        self.stdout.write(f'📦 Produtos: {Product.objects.count()}')
        self.stdout.write(f'🏷️ Categorias: {Category.objects.count()}')
        self.stdout.write(f'📏 Unidades: {Unit.objects.count()}')
        self.stdout.write(f'👥 Usuários: {User.objects.count()}')
        
        # Estatísticas de estoque
        critical = Product.objects.filter(current_stock=0).count()
        low = Product.objects.filter(
            current_stock__gt=0,
            current_stock__lte=models.F('min_stock')
        ).count()
        
        self.stdout.write(f'🔴 Estoque crítico: {critical}')
        self.stdout.write(f'🟡 Estoque baixo: {low}')
        
        self.stdout.write('\n🔑 ACESSO AO SISTEMA')
        self.stdout.write('Usuário: admin')
        self.stdout.write('Senha: admin123')
        self.stdout.write('URL: http://localhost:8000')
        self.stdout.write('='*50)