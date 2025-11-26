"""
Serializers para API REST de produtos.
"""
from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone

from .models import Category, Unit, Product


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para Category."""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'products_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Retorna quantidade de produtos na categoria."""
        return obj.products.filter(is_active=True).count()
    
    def validate_name(self, value):
        """Valida que o nome não está vazio."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nome não pode ser vazio.")
        return value.strip()


class UnitSerializer(serializers.ModelSerializer):
    """Serializer para Unit."""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id',
            'name',
            'description',
            'products_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Retorna quantidade de produtos na unidade."""
        return obj.products.filter(is_active=True).count()
    
    def validate_name(self, value):
        """Valida que o nome não está vazio."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nome não pode ser vazio.")
        return value.strip().upper()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de produtos."""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'category_name',
            'unit_name',
            'current_stock',
            'min_stock',
            'unit_price',
            'is_low_stock',
            'is_expired',
            'total_value',
            'expiry_date',
        ]
    
    def get_is_low_stock(self, obj):
        """Verifica se produto está com estoque baixo."""
        return obj.is_low_stock
    
    def get_is_expired(self, obj):
        """Verifica se produto está vencido."""
        return obj.is_expired
    
    def get_total_value(self, obj):
        """Calcula valor total em estoque."""
        if obj.unit_price and obj.current_stock:
            return float(obj.unit_price * obj.current_stock)
        return 0.0


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes de produtos."""
    
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True
    )
    
    unit = UnitSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source='unit',
        write_only=True
    )
    
    is_low_stock = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    movements_count = serializers.SerializerMethodField()
    last_movement_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'sku',
            'name',
            'description',
            'category',
            'category_id',
            'unit',
            'unit_id',
            'current_stock',
            'min_stock',
            'unit_price',
            'expiry_date',
            'ncm',
            'is_low_stock',
            'is_expired',
            'total_value',
            'movements_count',
            'last_movement_date',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'current_stock',
            'created_at',
            'updated_at',
        ]
    
    def get_is_low_stock(self, obj):
        """Verifica se produto está com estoque baixo."""
        return obj.is_low_stock
    
    def get_is_expired(self, obj):
        """Verifica se produto está vencido."""
        return obj.is_expired
    
    def get_total_value(self, obj):
        """Calcula valor total em estoque."""
        if obj.unit_price and obj.current_stock:
            return float(obj.unit_price * obj.current_stock)
        return 0.0
    
    def get_movements_count(self, obj):
        """Retorna quantidade de movimentações do produto."""
        return obj.movements.count()
    
    def get_last_movement_date(self, obj):
        """Retorna data da última movimentação."""
        last_movement = obj.movements.first()
        return last_movement.created_at if last_movement else None
    
    def validate_sku(self, value):
        """Valida SKU único."""
        if not value or not value.strip():
            raise serializers.ValidationError("SKU não pode ser vazio.")
        
        value = value.strip().upper()
        
        # Verifica duplicação (exceto no próprio objeto em update)
        qs = Product.objects.filter(sku=value, is_active=True)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        
        if qs.exists():
            raise serializers.ValidationError(f"SKU '{value}' já existe.")
        
        return value
    
    def validate_name(self, value):
        """Valida que o nome não está vazio."""
        if not value or not value.strip():
            raise serializers.ValidationError("Nome não pode ser vazio.")
        return value.strip()
    
    def validate_min_stock(self, value):
        """Valida estoque mínimo."""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Estoque mínimo não pode ser negativo.")
        return value
    
    def validate_unit_price(self, value):
        """Valida preço unitário."""
        if value is not None and value < Decimal('0.00'):
            raise serializers.ValidationError("Preço unitário não pode ser negativo.")
        return value
    
    def validate_expiry_date(self, value):
        """Valida data de validade."""
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Data de validade não pode ser no passado.")
        return value
    
    def validate(self, attrs):
        """Validações cross-field."""
        # Validação adicional se necessário
        return attrs


class ProductCreateSerializer(ProductDetailSerializer):
    """Serializer para criação de produtos (sem current_stock read-only)."""
    
    current_stock = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Estoque inicial do produto"
    )
    
    class Meta(ProductDetailSerializer.Meta):
        read_only_fields = ['id', 'created_at', 'updated_at']
