"""
ViewSets para API REST de produtos.
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, BooleanFilter
from django.db.models import Count, F

from .models import Category, Unit, Product
from .serializers import (
    CategorySerializer,
    UnitSerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
)
from core.permissions import IsAdminOrReadOnly, IsStaffUser


class CategoryFilter(FilterSet):
    """Filtros para Category."""
    name = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Category
        fields = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de categorias.
    
    list: Listar todas as categorias
    retrieve: Obter detalhes de uma categoria
    create: Criar nova categoria (apenas admin)
    update: Atualizar categoria (apenas admin)
    destroy: Remover categoria (soft delete - apenas admin)
    """
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Lista produtos de uma categoria."""
        category = self.get_object()
        products = category.products.filter(is_active=True)
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class UnitFilter(FilterSet):
    """Filtros para Unit."""
    name = CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Unit
        fields = ['name']


class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de unidades de medida.
    
    list: Listar todas as unidades
    retrieve: Obter detalhes de uma unidade
    create: Criar nova unidade (apenas admin)
    update: Atualizar unidade (apenas admin)
    destroy: Remover unidade (apenas admin)
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UnitFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ProductFilter(FilterSet):
    """Filtros para Product."""
    name = CharFilter(lookup_expr='icontains')
    sku = CharFilter(lookup_expr='icontains')
    category = NumberFilter(field_name='category__id')
    unit = NumberFilter(field_name='unit__id')
    min_stock_level = NumberFilter(field_name='current_stock', lookup_expr='lte', 
                                    label='Estoque <= min_stock (low stock)')
    low_stock = BooleanFilter(method='filter_low_stock', label='Estoque baixo')
    expired = BooleanFilter(method='filter_expired', label='Produto vencido')
    
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'unit']
    
    def filter_low_stock(self, queryset, name, value):
        """Filtra produtos com estoque baixo."""
        if value:
            return queryset.filter(current_stock__lte=F('min_stock'))
        return queryset
    
    def filter_expired(self, queryset, name, value):
        """Filtra produtos vencidos."""
        from django.utils import timezone
        if value:
            return queryset.filter(expiry_date__lt=timezone.now().date())
        return queryset


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gerenciamento de produtos.
    
    list: Listar todos os produtos
    retrieve: Obter detalhes de um produto
    create: Criar novo produto
    update: Atualizar produto
    partial_update: Atualizar parcialmente produto
    destroy: Remover produto (soft delete)
    
    Actions adicionais:
    - low_stock: Produtos com estoque baixo
    - expired: Produtos vencidos
    - stats: Estatísticas gerais de produtos
    """
    queryset = Product.objects.filter(is_active=True).select_related('category', 'unit')
    permission_classes = [IsAuthenticated, IsStaffUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description', 'ncm']
    ordering_fields = ['name', 'sku', 'current_stock', 'min_stock', 'unit_price', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Retorna serializer apropriado para a action."""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductDetailSerializer
    
    def perform_destroy(self, instance):
        """Soft delete do produto."""
        instance.soft_delete()
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Lista produtos com estoque abaixo do mínimo."""
        products = self.get_queryset().filter(current_stock__lte=F('min_stock'))
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Lista produtos vencidos."""
        from django.utils import timezone
        products = self.get_queryset().filter(expiry_date__lt=timezone.now().date())
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas gerais de produtos."""
        queryset = self.get_queryset()
        
        total_products = queryset.count()
        total_categories = queryset.values('category').distinct().count()
        total_stock_value = sum(
            (p.current_stock * p.unit_price) for p in queryset if p.unit_price
        )
        
        low_stock_count = queryset.filter(current_stock__lte=F('min_stock')).count()
        
        from django.utils import timezone
        expired_count = queryset.filter(expiry_date__lt=timezone.now().date()).count()
        
        stats = {
            'total_products': total_products,
            'total_categories': total_categories,
            'total_stock_value': float(total_stock_value),
            'low_stock_count': low_stock_count,
            'expired_count': expired_count,
            'top_categories': list(
                queryset.values('category__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5]
            ),
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def movements(self, request, pk=None):
        """Lista movimentações de um produto."""
        product = self.get_object()
        movements = product.movements.all()
        
        from movimentacoes.serializers import InventoryMovementListSerializer
        
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = InventoryMovementListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = InventoryMovementListSerializer(movements, many=True)
        return Response(serializer.data)
