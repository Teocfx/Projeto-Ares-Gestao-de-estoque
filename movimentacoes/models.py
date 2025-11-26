"""
Models para movimentações de estoque (entradas e saídas).
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.db import transaction
from decimal import Decimal
from typing import Any

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
            models.Index(fields=['product', '-created_at'], name='inv_mov_prod_date_idx'),
            models.Index(fields=['type', '-created_at'], name='inv_mov_type_date_idx'),
            models.Index(fields=['user', '-created_at'], name='inv_mov_user_date_idx'),
            # Índices compostos otimizados
            models.Index(fields=['product', 'type', '-created_at'], name='inv_mov_prod_type_date_idx'),
            models.Index(fields=['document'], name='inv_mov_document_idx'),
            models.Index(fields=['created_at'], name='inv_mov_created_idx'),
        ]

    def __str__(self) -> str:
        return f"{self.get_type_display()} - {self.product.name} ({self.quantity} {self.product.unit})"

    def get_absolute_url(self) -> str:
        """Retorna a URL de detalhes da movimentação."""
        return reverse('movimentacoes:detail', kwargs={'pk': self.pk})

    @property
    def url(self) -> str:
        """Alias para get_absolute_url (compatibilidade com Wagtail)."""
        return self.get_absolute_url()

    @property
    def title(self) -> str:
        """Retorna título formatado para busca."""
        return f"{self.get_type_display()}: {self.product.name} ({self.quantity} {self.product.unit})"

    @property
    def search_description(self) -> str:
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

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Salva a movimentação e atualiza o estoque do produto automaticamente.
        
        Este método sobrescreve o save padrão para:
        1. Garantir atomicidade da operação (transação)
        2. Evitar race conditions (lock do produto)
        3. Registrar estoque antes/depois para auditoria
        4. Validar estoque suficiente em saídas
        
        Args:
            *args: Argumentos posicionais para o save do Django
            **kwargs: Argumentos nomeados para o save do Django
        
        Raises:
            ValidationError: Quando estoque é insuficiente para saída
        
        Examples:
            >>> movement = InventoryMovement(product=prod, type='ENTRADA', quantity=10)
            >>> movement.save()  # Estoque aumenta em 10 unidades
            
            >>> movement = InventoryMovement(product=prod, type='SAIDA', quantity=5)
            >>> movement.save()  # Estoque reduz em 5 unidades
        """
        with transaction.atomic():
            # Carrega o produto com lock para evitar race conditions
            product = self._get_locked_product()
            
            # Registra estoque anterior para auditoria
            self.stock_before = product.current_stock
            
            # Atualiza o estoque baseado no tipo de movimentação
            self._update_product_stock(product)
            
            # Registra estoque posterior para auditoria
            self.stock_after = product.current_stock
            
            # Salva o produto e a movimentação
            product.save()
            super().save(*args, **kwargs)
    
    def _get_locked_product(self):
        """
        Obtém o produto com lock de linha para evitar race conditions.
        
        Returns:
            Product: Produto com lock SELECT FOR UPDATE
        
        Notes:
            - Se a movimentação já existe (tem pk), recarrega do banco
            - Se é nova, usa a instância já carregada
        """
        if self.pk:
            return type(self).objects.select_for_update().get(pk=self.product.pk)
        return self.product
    
    def _update_product_stock(self, product) -> None:
        """
        Atualiza o estoque do produto baseado no tipo de movimentação.
        
        Args:
            product: Instância do produto a ser atualizado
        
        Raises:
            ValidationError: Se estoque for insuficiente para saída
        
        Notes:
            - ENTRADA: Adiciona quantidade ao estoque atual
            - SAIDA: Subtrai quantidade (valida disponibilidade)
            - AJUSTE: Define quantidade como valor absoluto
        """
        from django.core.exceptions import ValidationError
        
        if self.type == self.ENTRADA:
            product.current_stock += self.quantity
        elif self.type == self.SAIDA:
            self._validate_stock_availability(product)
            product.current_stock -= self.quantity
        elif self.type == self.AJUSTE:
            product.current_stock = self.quantity
    
    def _validate_stock_availability(self, product) -> None:
        """
        Valida se há estoque suficiente para uma saída.
        
        Args:
            product: Produto a validar disponibilidade
        
        Raises:
            ValidationError: Se estoque atual for menor que quantidade solicitada
        """
        from django.core.exceptions import ValidationError
        
        if product.current_stock < self.quantity:
            raise ValidationError(
                f"Estoque insuficiente. Disponível: {product.current_stock} {product.unit}"
            )

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
