"""
Comando aprimorado para popular movimentações de teste no banco de dados.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import timedelta, datetime

from produtos.models import Product
from movimentacoes.models import InventoryMovement


class Command(BaseCommand):
    help = 'Popula o banco de dados com movimentações de teste realistas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=200,
            help='Número total de movimentações a criar (padrão: 200)'
        )

        parser.add_argument(
            '--days',
            type=int,
            default=120,
            help='Período em dias para distribuir as movimentações (padrão: 120 dias)'
        )

        parser.add_argument(
            '--product',
            type=str,
            help='Gerar movimentações apenas para um SKU específico'
        )

        parser.add_argument(
            '--user',
            type=int,
            help='ID de usuário fixo para registrar as movimentações'
        )

    def handle(self, *args, **options):
        user_model = get_user_model()

        count = options['count']
        days_back = options['days']
        filter_sku = options.get("product")
        fixed_user_id = options.get("user")

        self.stdout.write("🔄 Iniciando geração de movimentações realistas...\n")

        # Produtos-alvo
        if filter_sku:
            products = list(Product.objects.filter(sku=filter_sku, is_active=True))
        else:
            products = list(Product.objects.filter(is_active=True))

        if not products:
            self.stdout.write(self.style.ERROR("Nenhum produto encontrado!"))
            return

        # Usuários
        if fixed_user_id:
            users = [user_model.objects.get(pk=fixed_user_id)]
        else:
            users = list(user_model.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("Nenhum usuário disponível!"))
            return

        # Prefixos
        document_prefixes = ["NF", "NFe", "CF-e", "NFS-e", "REQ", "TRF"]
        notes_by_type = {
            InventoryMovement.ENTRADA: [
                "Entrada de fornecedor",
                "Reposição de estoque",
                "Compra regular",
                "Entrada por transferência",
                "Devolução de venda"
            ],
            InventoryMovement.SAIDA: [
                "Venda balcão",
                "Baixa por consumo interno",
                "Transferência entre setores",
                "Saída para cliente especial",
            ],
            InventoryMovement.AJUSTE: [
                "Quebra identificada",
                "Inventário – ajuste negativo",
                "Inventário – ajuste positivo",
                "Correção de estoque incorreto",
                "Perda por validade vencida"
            ],
            InventoryMovement.INVENTARIO: [
                "Inventário físico geral",
                "Inventário rotativo",
                "Ajuste por contagem oficial"
            ]
        }

        # Estatísticas iniciais
        total_stock_before = sum(float(p.current_stock) for p in products)

        movements_created = 0

        with transaction.atomic():

            for i in range(count):
                try:
                    product = random.choice(products)

                    # Probabilidades mais realistas
                    movement_type = random.choices(
                        population=[
                            InventoryMovement.ENTRADA,
                            InventoryMovement.SAIDA,
                            InventoryMovement.AJUSTE,
                            InventoryMovement.INVENTARIO
                        ],
                        weights=[40, 40, 15, 5],  # entradas e saídas predominam
                        k=1
                    )[0]

                    # QUANTIDADES
                    if movement_type == InventoryMovement.ENTRADA:
                        quantity = Decimal(random.uniform(3, 80))

                    elif movement_type == InventoryMovement.SAIDA:
                        if product.current_stock <= 0:
                            continue
                        max_qty = float(product.current_stock)
                        quantity = Decimal(random.uniform(1, max(1, max_qty / 2)))

                    elif movement_type == InventoryMovement.AJUSTE:
                        # 70% chance de ajuste negativo
                        if random.random() < 0.7:
                            quantity = Decimal(random.uniform(0.1, 10))
                        else:
                            quantity = Decimal(random.uniform(0.1, 15))

                    else:  # INVENTARIO
                        # O inventário define um novo valor de estoque
                        new_stock = Decimal(random.uniform(0, 150))
                        quantity = abs(product.current_stock - new_stock)

                    # Documento (80% possuem)
                    document = ""
                    if random.random() < 0.8:
                        prefix = random.choice(document_prefixes)
                        number = random.randint(10000, 999999)
                        document = f"{prefix}-{number}"

                    # Nota (70% possuem)
                    notes = ""
                    if random.random() < 0.7:
                        notes = random.choice(notes_by_type[movement_type])

                    # Data aleatória + hora aleatória
                    days_ago = random.randint(0, days_back)
                    dt = timezone.now() - timedelta(
                        days=days_ago,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )

                    user = random.choice(users)

                    # Criar movimentação
                    movement = InventoryMovement(
                        product=product,
                        type=movement_type,
                        quantity=quantity,
                        document=document,
                        notes=notes,
                        user=user,
                        created_at=dt
                    )

                    movement.save()
                    movements_created += 1

                    if movements_created % 30 == 0:
                        self.stdout.write(f"✓ {movements_created} movimentações criadas...")

                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"⚠ Erro ao criar movimentação: {e}"))
                    continue

        # Estatísticas
        total_stock_after = sum(float(p.current_stock) for p in products)

        self.stdout.write(self.style.SUCCESS(f"\n🎉 {movements_created} movimentações criadas com sucesso!\n"))

        entradas = InventoryMovement.objects.filter(type=InventoryMovement.ENTRADA).count()
        saidas = InventoryMovement.objects.filter(type=InventoryMovement.SAIDA).count()
        ajustes = InventoryMovement.objects.filter(type=InventoryMovement.AJUSTE).count()
        inventarios = InventoryMovement.objects.filter(type=InventoryMovement.INVENTARIO).count()

        self.stdout.write("📊 Estatísticas:")
        self.stdout.write(f"Entradas: {entradas}")
        self.stdout.write(f"Saídas: {saidas}")
        self.stdout.write(f"Ajustes: {ajustes}")
        self.stdout.write(f"Inventários: {inventarios}")

        self.stdout.write(f"\n📦 Estoque total antes: {total_stock_before:.2f}")
        self.stdout.write(f"📦 Estoque total depois: {total_stock_after:.2f}")

        self.stdout.write(self.style.SUCCESS("\n✔ População concluída!\n"))
