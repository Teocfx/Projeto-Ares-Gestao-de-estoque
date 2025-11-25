"""
Serializers para API REST de movimentações.
"""
from rest_framework import serializers
from decimal import Decimal
from django.db import transaction

from .models import InventoryMovement
from produtos.serializers import ProductListSerializer


class InventoryMovementListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de movimentações."""
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    unit_name = serializers.CharField(source='product.unit.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id',
            'product_name',
            'product_sku',
            'type',
            'type_display',
            'quantity',
            'unit_name',
            'document',
            'user_name',
            'user_username',
            'stock_before',
            'stock_after',
            'created_at',
        ]


class InventoryMovementDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalhes de movimentações."""
    
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = InventoryMovement
        fields = [
            'id',
            'product',
            'product_id',
            'type',
            'type_display',
            'quantity',
            'document',
            'notes',
            'user_name',
            'user_username',
            'stock_before',
            'stock_after',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user_name',
            'user_username',
            'stock_before',
            'stock_after',
            'created_at',
            'updated_at',
        ]
    
    def validate_product_id(self, value):
        """Valida que o produto existe e está ativo."""
        from produtos.models import Product
        try:
            product = Product.objects.get(id=value, is_active=True)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Produto não encontrado ou inativo.")
    
    def validate_quantity(self, value):
        """Valida quantidade positiva."""
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Quantidade deve ser maior que zero.")
        return value
    
    def validate(self, attrs):
        """Validações cross-field e de negócio."""
        from produtos.models import Product
        
        product_id = attrs.get('product_id')
        movement_type = attrs.get('type')
        quantity = attrs.get('quantity')
        
        # Buscar produto
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': 'Produto não encontrado ou foi removido.'
            })
        
        # Para saídas, validar estoque suficiente
        if movement_type == InventoryMovement.SAIDA:
            if quantity > product.current_stock:
                raise serializers.ValidationError({
                    'quantity': f'Estoque insuficiente. Disponível: {product.current_stock} {product.unit.name}'
                })
        
        # Adicionar produto ao attrs para uso no create
        attrs['product'] = product
        
        return attrs
    
    def create(self, validated_data):
        """Cria movimentação e atualiza estoque automaticamente."""
        # Usuário vem do contexto (view adiciona)
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Criar movimentação com atualização de estoque
        with transaction.atomic():
            movement = InventoryMovement.objects.create(**validated_data)
        
        return movement


class InventoryMovementBulkSerializer(serializers.Serializer):
    """Serializer para criação em lote de movimentações."""
    
    movements = serializers.ListField(
        child=InventoryMovementDetailSerializer(),
        min_length=1,
        max_length=100,
        help_text="Lista de movimentações (máximo 100)"
    )
    
    def create(self, validated_data):
        """Cria múltiplas movimentações em transação única."""
        movements_data = validated_data['movements']
        user = self.context['request'].user
        
        created_movements = []
        with transaction.atomic():
            for movement_data in movements_data:
                movement_data['user'] = user
                movement = InventoryMovement.objects.create(**movement_data)
                created_movements.append(movement)
        
        return {'movements': created_movements, 'count': len(created_movements)}


class InventoryMovementStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de movimentações."""
    
    total_movements = serializers.IntegerField()
    total_entries = serializers.IntegerField()
    total_exits = serializers.IntegerField()
    total_adjustments = serializers.IntegerField()
    quantity_entered = serializers.DecimalField(max_digits=15, decimal_places=2)
    quantity_exited = serializers.DecimalField(max_digits=15, decimal_places=2)
    most_moved_products = serializers.ListField()
    recent_movements = InventoryMovementListSerializer(many=True)
