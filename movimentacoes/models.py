"""
Models para movimentações de estoque (entradas e saídas).
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.db import transaction
from decimal import Decimal

from core.models import TimeStampedModel


class InventoryMovement(TimeStampedModel):
    """
    Movimentação de estoque (entrada/saída).
    Atualiza automaticamente o estoque do produto.
    """
    
    # Tipos de movimentação
    ENTRADA = 'ENTRADA'
    SAIDA = 'SAIDA'
    AJUSTE = 'AJUSTE'
    
    TYPE_CHOICES = [
        (ENTRADA, 'Entrada'),
        (SAIDA, 'Saída'),
        (AJUSTE, 'Ajuste'),
    ]
    
    # Dados da movimentação
    product = models.ForeignKey(
        'produtos.Product',
        on_delete=models.PROTECT,
        related_name='movements',
        verbose_name="Produto"
    )
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        verbose_name="Tipo"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Quantidade"
    )
    
    # Documentação
    document = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Documento",
        help_text="Número da NF, CF-e, ou outro documento"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observações"
    )
    
    # Auditoria
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='inventory_movements',
        verbose_name="Usuário"
    )
    
    # Estoque antes/depois (para auditoria)
    stock_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Estoque Anterior"
    )
    stock_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Estoque Posterior"
    )

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.product.name} ({self.quantity} {self.product.unit})"

    def get_absolute_url(self):
        """Retorna a URL de detalhes da movimentação."""
        return reverse('movimentacoes:detail', kwargs={'pk': self.pk})

    @property
    def url(self):
        """Alias para get_absolute_url (compatibilidade com Wagtail)."""
        return self.get_absolute_url()

    @property
    def title(self):
        """Retorna título formatado para busca."""
        return f"{self.get_type_display()}: {self.product.name} ({self.quantity} {self.product.unit})"

    @property
    def search_description(self):
        """Retorna descrição formatada para resultados de busca."""
        desc_parts = []
        desc_parts.append(f"Produto: {self.product.sku} - {self.product.name}")
        desc_parts.append(f"Quantidade: {self.quantity} {self.product.unit}")
        desc_parts.append(f"Estoque: {self.stock_before} → {self.stock_after}")
        if self.document:
            desc_parts.append(f"Documento: {self.document}")
        if self.notes:
            desc_parts.append(f"Obs: {self.notes[:100]}")
        return " | ".join(desc_parts)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o save para atualizar o estoque do produto automaticamente.
        Usa transaction.atomic() para garantir consistência.
        """
        with transaction.atomic():
            # Carrega o produto com lock para evitar race conditions
            product = type(self).objects.select_for_update().get(
                pk=self.product.pk
            ) if self.pk else self.product
            
            # Guarda estoque anterior
            self.stock_before = product.current_stock
            
            # Atualiza o estoque baseado no tipo de movimentação
            if self.type == self.ENTRADA:
                product.current_stock += self.quantity
            elif self.type == self.SAIDA:
                # Verifica se há estoque suficiente
                if product.current_stock < self.quantity:
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        f"Estoque insuficiente. Disponível: {product.current_stock} {product.unit}"
                    )
                product.current_stock -= self.quantity
            elif self.type == self.AJUSTE:
                # Ajuste pode ser positivo ou negativo
                # A quantidade representa o valor final desejado, não a diferença
                product.current_stock = self.quantity
            
            # Guarda estoque posterior
            self.stock_after = product.current_stock
            
            # Salva o produto
            product.save()
            
            # Salva a movimentação
            super().save(*args, **kwargs)

    @property
    def difference(self):
        """Retorna a diferença de estoque (stock_after - stock_before)."""
        return self.stock_after - self.stock_before


class StockLocation(TimeStampedModel):
    """
    Localização física do estoque (para futuras expansões).
    Ex: Depósito A, Prateleira 3, Setor B
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )

    class Meta:
        verbose_name = "Localização de Estoque"
        verbose_name_plural = "Localizações de Estoque"
        ordering = ['name']

    def __str__(self):
        return self.name
