"""
Models para gerenciamento de produtos.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from decimal import Decimal
from typing import Optional

from core.models import TimeStampedModel, SoftDeleteModel


class Category(TimeStampedModel, SoftDeleteModel):
    """Categoria de produtos."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nome"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Retorna a URL da lista de produtos desta categoria."""
        return reverse('produtos:list') + f'?category={self.pk}'

    @property
    def url(self):
        """Alias para get_absolute_url (compatibilidade com Wagtail)."""
        return self.get_absolute_url()

    @property
    def title(self):
        """Retorna o nome como title (compatibilidade com busca)."""
        return self.name

    @property
    def search_description(self) -> str:
        """Retorna a descrição para resultados de busca."""
        return self.description or f"Categoria de produtos: {self.name}"


class Unit(TimeStampedModel):
    """Unidade de medida (UN, KG, L, etc)."""
    name = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Nome",
        help_text="Ex: UN, KG, L, CX"
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Descrição",
        help_text="Ex: Unidade, Quilograma, Litro"
    )

    class Meta:
        verbose_name = "Unidade de Medida"
        verbose_name_plural = "Unidades de Medida"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(TimeStampedModel, SoftDeleteModel):
    """Produto do estoque."""
    
    # Identificação
    sku = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Código/SKU",
        help_text="Código único do produto"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nome"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    # Relacionamentos
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Categoria"
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Unidade"
    )
    
    # Estoque
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estoque Atual"
    )
    min_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Estoque Mínimo",
        help_text="Nível mínimo de estoque antes de alerta"
    )
    
    # Financeiro
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Preço Unitário"
    )
    
    # Validade
    expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Validade"
    )
    
    # Dados fiscais (opcional)
    ncm = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="NCM",
        help_text="Nomenclatura Comum do Mercosul"
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['name']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['category', 'name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.sku} — {self.name}"

    def get_absolute_url(self):
        """Retorna a URL de detalhes do produto."""
        return reverse('produtos:detail', kwargs={'pk': self.pk})

    @property
    def url(self):
        """Alias para get_absolute_url (compatibilidade com Wagtail)."""
        return self.get_absolute_url()

    @property
    def title(self):
        """Retorna o nome como title (compatibilidade com busca)."""
        return f"{self.sku} - {self.name}"

    @property
    def search_description(self) -> str:
        """Retorna descrição formatada para resultados de busca."""
        desc_parts = []
        if self.description:
            desc_parts.append(self.description[:150])
        desc_parts.append(f"Categoria: {self.category.name}")
        desc_parts.append(f"Estoque: {self.current_stock} {self.unit.name}")
        desc_parts.append(f"Status: {self.stock_status_display}")
        return " | ".join(desc_parts)

    @property
    def stock_status(self) -> str:
        """
        Retorna o status do estoque.
        Retorna: 'CRITICO', 'BAIXO', 'OK'
        """
        if self.current_stock == 0:
            return "CRITICO"
        elif self.current_stock <= self.min_stock:
            return "BAIXO"
        return "OK"

    @property
    def stock_status_display(self) -> str:
        """Retorna o status formatado para exibição."""
        status_map = {
            'CRITICO': '🔴 Crítico',
            'BAIXO': '🟡 Baixo',
            'OK': '🟢 OK'
        }
        return status_map.get(self.stock_status, 'OK')

    @property
    def expiry_status(self) -> Optional[str]:
        """
        Verifica o status de validade do produto.
        Retorna: 'VENCIDO', 'PROXIMO', 'OK', None (sem validade)
        """
        if not self.expiry_date:
            return None
        
        today = timezone.now().date()
        days_until_expiry = (self.expiry_date - today).days
        
        if days_until_expiry < 0:
            return "VENCIDO"
        elif days_until_expiry <= 7:
            return "PROXIMO"
        return "OK"

    @property
    def total_value(self) -> Decimal:
        """Valor total do estoque (estoque atual * preço unitário)."""
        if self.unit_price:
            return self.current_stock * self.unit_price
        return Decimal('0.00')

    def has_low_stock(self) -> bool:
        """Verifica se o estoque está baixo ou crítico."""
        return self.stock_status in ['BAIXO', 'CRITICO']

    def is_expired(self) -> bool:
        """Verifica se o produto está vencido."""
        return self.expiry_status == 'VENCIDO'

    def is_near_expiry(self) -> bool:
        """Verifica se o produto está próximo do vencimento."""
        return self.expiry_status == 'PROXIMO'
