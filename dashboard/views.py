"""
Views do Dashboard.
Dashboard principal com métricas e estatísticas do sistema.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count, Q
from decimal import Decimal
from datetime import datetime, timedelta

# Importar models dos apps (com fallback se não existirem)
try:
    from produtos.models import Product, Category
    PRODUCTS_AVAILABLE = True
except ImportError:
    PRODUCTS_AVAILABLE = False

try:
    from movimentacoes.models import InventoryMovement
    MOVEMENTS_AVAILABLE = True
except ImportError:
    MOVEMENTS_AVAILABLE = False


@login_required
def index(request):
    """Dashboard principal com estatísticas em tempo real."""
    
    # Inicializar contexto
    context = {
        'title': 'Dashboard - Sistema ARES',
        'user': request.user,
    }
    
    # Estatísticas de produtos (se disponível)
    if PRODUCTS_AVAILABLE:
        # Produtos básicos
        total_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.count()
        
        # Status de estoque
        critical_stock = Product.objects.filter(
            is_active=True,
            current_stock=0
        ).count()
        
        low_stock = Product.objects.filter(
            is_active=True,
            current_stock__gt=0,
            current_stock__lte=F('min_stock')
        ).count()
        
        ok_stock = total_products - critical_stock - low_stock
        
        # Valor total do estoque
        total_stock_value = Product.objects.filter(
            is_active=True,
            unit_price__isnull=False
        ).aggregate(
            total=Sum(F('current_stock') * F('unit_price'))
        )['total'] or Decimal('0')
        
        # Produtos críticos para exibir
        critical_products = Product.objects.filter(
            is_active=True,
            current_stock=0
        ).select_related('category', 'unit')[:5]
        
        # Produtos com estoque baixo
        low_stock_products = Product.objects.filter(
            is_active=True,
            current_stock__gt=0,
            current_stock__lte=F('min_stock')
        ).select_related('category', 'unit')[:5]
        
        # Produtos próximos do vencimento (próximos 30 dias)
        thirty_days_from_now = datetime.now().date() + timedelta(days=30)
        expiring_products = Product.objects.filter(
            is_active=True,
            expiry_date__lte=thirty_days_from_now,
            expiry_date__gt=datetime.now().date()
        ).select_related('category', 'unit')[:5]
        
        context.update({
            'products_stats': {
                'total_products': total_products,
                'total_categories': total_categories,
                'critical_stock': critical_stock,
                'low_stock': low_stock,
                'ok_stock': ok_stock,
                'total_stock_value': total_stock_value,
            },
            'critical_products': critical_products,
            'low_stock_products': low_stock_products,
            'expiring_products': expiring_products,
        })
    
    # Estatísticas de movimentações (se disponível)
    if MOVEMENTS_AVAILABLE:
        # Movimentações dos últimos 30 dias
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        
        recent_movements_count = InventoryMovement.objects.filter(
            created_at__date__gte=thirty_days_ago
        ).count()
        
        # Últimas movimentações
        recent_movements = InventoryMovement.objects.select_related(
            'product', 'user'
        ).order_by('-created_at')[:10]
        
        context.update({
            'movements_stats': {
                'recent_movements_count': recent_movements_count,
            },
            'recent_movements': recent_movements,
        })
    
    # Informações do sistema
    context.update({
        'system_info': {
            'products_available': PRODUCTS_AVAILABLE,
            'movements_available': MOVEMENTS_AVAILABLE,
            'current_time': datetime.now(),
        },
        # URLs para os cards
        'produtos_list_url': '/produtos/',
        'produtos_baixo_url': '/produtos/?stock_status=BAIXO',
        'produtos_critico_url': '/produtos/?stock_status=CRITICO',
    })
    
    return render(request, 'dashboard/index.html', context)
