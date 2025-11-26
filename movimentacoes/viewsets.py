"""
ViewSets para API REST de movimentações.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, DateFilter
from django.db.models import Sum, Count

from .models import InventoryMovement
from .serializers import (
    InventoryMovementListSerializer,
    InventoryMovementDetailSerializer,
    InventoryMovementBulkSerializer,
    InventoryMovementStatsSerializer,
)
from core.permissions import IsStaffUser


class InventoryMovementFilter(FilterSet):
    """Filtros para InventoryMovement."""
    product = NumberFilter(field_name='product__id')
    product_name = CharFilter(field_name='product__name', lookup_expr='icontains')
    product_sku = CharFilter(field_name='product__sku', lookup_expr='icontains')
    type = CharFilter(field_name='type')
    user = NumberFilter(field_name='user__id')
    date_from = DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = DateFilter(field_name='created_at', lookup_expr='lte')
    document = CharFilter(field_name='document', lookup_expr='icontains')
    
    class Meta:
        model = InventoryMovement
        fields = ['product', 'type', 'user']


class InventoryMovementViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gerenciamento de movimentações de estoque.
    
    list: Listar todas as movimentações
    retrieve: Obter detalhes de uma movimentação
    create: Criar nova movimentação (atualiza estoque automaticamente)
    
    Actions adicionais:
    - bulk_create: Criar múltiplas movimentações em lote
    - stats: Estatísticas de movimentações
    - by_product: Movimentações de um produto específico
    - by_type: Movimentações por tipo
    """
    queryset = InventoryMovement.objects.all().select_related('product', 'product__unit', 'user')
    permission_classes = [IsAuthenticated, IsStaffUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = InventoryMovementFilter
    search_fields = ['product__name', 'product__sku', 'document', 'notes']
    ordering_fields = ['created_at', 'quantity', 'type']
    ordering = ['-created_at']
    
    # Movimentações não podem ser editadas ou deletadas (auditoria)
    http_method_names = ['get', 'post', 'head', 'options']
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para a action."""
        if self.action == 'list':
            return InventoryMovementListSerializer
        elif self.action == 'bulk_create':
            return InventoryMovementBulkSerializer
        return InventoryMovementDetailSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Cria múltiplas movimentações em lote (máximo 100).
        
        Exemplo de body:
        {
            "movements": [
                {"product_id": 1, "type": "ENTRADA", "quantity": 10, "document": "NF-001"},
                {"product_id": 2, "type": "SAIDA", "quantity": 5, "notes": "Venda"}
            ]
        }
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        
        return Response({
            'message': f'{result["count"]} movimentações criadas com sucesso.',
            'count': result['count'],
            'movements': InventoryMovementListSerializer(result['movements'], many=True).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas de movimentações."""
        queryset = self.get_queryset()
        
        # Filtrar por período se fornecido
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        total_movements = queryset.count()
        total_entries = queryset.filter(type=InventoryMovement.ENTRADA).count()
        total_exits = queryset.filter(type=InventoryMovement.SAIDA).count()
        total_adjustments = queryset.filter(type=InventoryMovement.AJUSTE).count()
        
        quantity_entered = queryset.filter(
            type=InventoryMovement.ENTRADA
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        quantity_exited = queryset.filter(
            type=InventoryMovement.SAIDA
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0
        
        most_moved_products = list(
            queryset.values('product__name', 'product__sku')
            .annotate(total_quantity=Sum('quantity'), count=Count('id'))
            .order_by('-total_quantity')[:10]
        )
        
        recent_movements = queryset[:10]
        
        stats = {
            'total_movements': total_movements,
            'total_entries': total_entries,
            'total_exits': total_exits,
            'total_adjustments': total_adjustments,
            'quantity_entered': quantity_entered,
            'quantity_exited': quantity_exited,
            'most_moved_products': most_moved_products,
            'recent_movements': recent_movements,
        }
        
        serializer = InventoryMovementStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Lista movimentações de um produto específico."""
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movements = self.get_queryset().filter(product_id=product_id)
        
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Lista movimentações por tipo (ENTRADA, SAIDA, AJUSTE)."""
        movement_type = request.query_params.get('type')
        
        if not movement_type:
            return Response(
                {'error': 'type é obrigatório (ENTRADA, SAIDA, AJUSTE).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if movement_type not in dict(InventoryMovement.TYPE_CHOICES):
            return Response(
                {'error': f'Tipo inválido. Valores permitidos: ENTRADA, SAIDA, AJUSTE.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        movements = self.get_queryset().filter(type=movement_type)
        
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(movements, many=True)
        return Response(serializer.data)
