"""
Comando para popular movimentações de teste no banco de dados.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta

from produtos.models import Product
from movimentacoes.models import InventoryMovement


class Command(BaseCommand):
    help = 'Popula o banco de dados com movimentações de teste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Número de movimentações a criar (padrão: 100)'
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Período em dias para distribuir as movimentações (padrão: 90)'
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        
        count = options['count']
        days_back = options['days']
        
        self.stdout.write('Iniciando população de movimentações...')
        
        # Verificar se existem produtos e usuários
        products = list(Product.objects.filter(is_active=True))
        users = list(user_model.objects.all())
        
        if not products:
            self.stdout.write(
                self.style.ERROR('Nenhum produto encontrado. Execute primeiro o populate_products.')
            )
            return
            
        if not users:
            self.stdout.write(
                self.style.ERROR('Nenhum usuário encontrado. Crie um superuser primeiro.')
            )
            return
        
        # Dados para movimentações realistas
        document_prefixes = ['NF', 'CF-e', 'NFS-e', 'CT-e', 'REQ']
        notes_templates = [
            'Entrada de mercadoria do fornecedor',
            'Saída para venda no balcão',
            'Ajuste de inventário',
            'Transferência entre estoques',
            'Devolução de cliente',
            'Quebra identificada no estoque',
            'Compra para reposição',
            'Venda para cliente especial',
        ]
        
        movements_created = 0
        
        with transaction.atomic():
            for i in range(count):
                try:
                    # Produto aleatório
                    product = random.choice(products)
                    
                    # Tipo de movimentação (mais entradas no início, mais saídas depois)
                    if i < count * 0.3:  # 30% entradas iniciais
                        movement_type = InventoryMovement.ENTRADA
                    elif i < count * 0.7:  # 40% saídas
                        movement_type = InventoryMovement.SAIDA
                    else:  # 30% mix de todos os tipos
                        movement_type = random.choice([
                            InventoryMovement.ENTRADA,
                            InventoryMovement.SAIDA,
                            InventoryMovement.AJUSTE
                        ])
                    
                    # Quantidade baseada no tipo
                    if movement_type == InventoryMovement.ENTRADA:
                        quantity = Decimal(str(random.uniform(5, 50)))
                    elif movement_type == InventoryMovement.SAIDA:
                        # Garantir que não saia mais do que tem
                        max_quantity = min(product.current_stock, Decimal('20'))
                        if max_quantity > 0:
                            quantity = Decimal(str(random.uniform(0.1, float(max_quantity))))
                        else:
                            continue  # Pular se não há estoque
                    else:  # AJUSTE
                        quantity = Decimal(str(random.uniform(0, 30)))
                    
                    # Documento (70% das movimentações têm documento)
                    document = ''
                    if random.random() < 0.7:
                        prefix = random.choice(document_prefixes)
                        number = random.randint(100000, 999999)
                        document = f'{prefix}-{number}'
                    
                    # Observações (50% têm observações)
                    notes = ''
                    if random.random() < 0.5:
                        notes = random.choice(notes_templates)
                    
                    # Data aleatória no período
                    days_ago = random.randint(0, days_back)
                    created_at = timezone.now() - timedelta(days=days_ago)
                    
                    # Usuário aleatório
                    user = random.choice(users)
                    
                    # Criar movimentação
                    movement = InventoryMovement(
                        product=product,
                        type=movement_type,
                        quantity=quantity,
                        document=document,
                        notes=notes,
                        user=user,
                        created_at=created_at
                    )
                    
                    # O save() vai atualizar o estoque automaticamente
                    movement.save()
                    movements_created += 1
                    
                    if movements_created % 20 == 0:
                        self.stdout.write(f'Criadas {movements_created} movimentações...')
                        
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'Erro ao criar movimentação {i}: {str(e)}')
                    )
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {movements_created} movimentações criadas com sucesso!')
        )
        
        # Estatísticas finais
        total_movements = InventoryMovement.objects.count()
        entradas = InventoryMovement.objects.filter(type=InventoryMovement.ENTRADA).count()
        saidas = InventoryMovement.objects.filter(type=InventoryMovement.SAIDA).count()
        ajustes = InventoryMovement.objects.filter(type=InventoryMovement.AJUSTE).count()
        
        self.stdout.write('\n📊 Estatísticas finais:')
        self.stdout.write(f'Total de movimentações: {total_movements}')
        self.stdout.write(f'Entradas: {entradas}')
        self.stdout.write(f'Saídas: {saidas}')
        self.stdout.write(f'Ajustes: {ajustes}')
        
        # Produtos com estoque atualizado
        products_updated = Product.objects.filter(is_active=True).count()
        self.stdout.write(f'Produtos com estoque atualizado: {products_updated}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 População de movimentações concluída!')
        )