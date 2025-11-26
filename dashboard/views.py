"""
Views do Dashboard.
Dashboard principal com métricas e estatísticas do sistema.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Count, Q
from django.views.decorators.cache import cache_page
from django.core.cache import cache
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
@cache_page(60 * 2)  # Cache de 2 minutos (dashboard com dados relativamente estáticos)
def index(request):
    """
    Dashboard principal com estatísticas em tempo real.
    
    Exibe métricas gerais do sistema incluindo:
    - Total de produtos e categorias
    - Status de estoque (crítico, baixo, OK)
    - Valor total do estoque
    - Produtos com estoque crítico ou baixo
    - Produtos próximos ao vencimento
    - Movimentações recentes
    - Gráficos de movimentações diárias
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Dashboard renderizado com todas as métricas
    
    Notes:
        - Cache de 2 minutos para reduzir carga no banco
        - Queries otimizadas com select_related
        - Estatísticas calculadas dinamicamente
    """
    
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
        
        # Produtos com estoque baixo ou crítico (inclui estoque = 0)
        low_stock_products = Product.objects.filter(
            is_active=True,
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


@login_required
def get_filter_options(request):
    """Retorna opções para os filtros (produtos, categorias, usuários)."""
    from django.http import JsonResponse
    
    data = {}
    
    # Produtos
    if PRODUCTS_AVAILABLE:
        from produtos.models import Product
        products = Product.objects.filter(is_active=True).values('id', 'sku', 'name').order_by('name')[:100]
        data['products'] = [{'id': p['id'], 'label': f"{p['sku']} - {p['name']}"} for p in products]
        
        # Categorias
        categories = Category.objects.all().values('id', 'name').order_by('name')
        data['categories'] = [{'id': c['id'], 'label': c['name']} for c in categories]
    else:
        data['products'] = []
        data['categories'] = []
    
    # Usuários que fizeram movimentações
    if MOVEMENTS_AVAILABLE:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(
            inventory_movements__isnull=False
        ).distinct().values('id', 'username', 'first_name', 'last_name').order_by('username')
        data['users'] = [{
            'id': u['id'],
            'label': f"{u['first_name']} {u['last_name']}" if u['first_name'] else u['username']
        } for u in users]
    else:
        data['users'] = []
    
    return JsonResponse(data)


@login_required
def get_chart_data(request):
    """
    Retornar dados do gráfico de movimentações via AJAX com filtros avançados.
    
    Filtros disponíveis:
    - period: 7d, 1m, 3m, 6m, 1y, este_mes, mes_passado, este_ano, ano_passado, 
              ultimos_2anos, ultimos_5anos, q1, q2, q3, q4, custom
    - movement_type: ENTRADA, SAIDA, AJUSTE (pode enviar múltiplos separados por vírgula)
    - product_id: ID do produto
    - category_id: ID da categoria
    - user_id: ID do usuário
    - search: busca por texto (produto, SKU, documento, notas)
    - min_quantity: quantidade mínima
    - max_quantity: quantidade máxima
    - sort_by: date, quantity, type, product (default: date)
    - sort_order: asc, desc (default: desc)
    """
    from django.http import JsonResponse
    from collections import defaultdict
    
    period = request.GET.get('period', '7d')  # 7d, 1m, 3m, 6m, 1y, custom, etc.
    
    if not MOVEMENTS_AVAILABLE:
        return JsonResponse({
            'labels': [],
            'entradas': [],
            'saidas': [],
            'title': 'Movimentações'
        })
    
    # Definir período e agrupamento
    now = datetime.now()
    today = now.date()
    
    # Períodos básicos (já existentes)
    if period == '7d':
        start_date = today - timedelta(days=7)
        group_by = 'day'
        title = 'Últimos 7 Dias'
    elif period == '1m':
        start_date = today - timedelta(days=30)
        group_by = 'week'
        title = 'Últimos 30 Dias'
    elif period == '3m':
        start_date = today - timedelta(days=90)
        group_by = 'month'
        title = 'Últimos 3 Meses'
    elif period == '6m':
        start_date = today - timedelta(days=180)
        group_by = 'month'
        title = 'Últimos 6 Meses'
    elif period == '1y':
        start_date = today - timedelta(days=365)
        group_by = 'month'
        title = 'Último Ano'
    
    # Períodos por mês
    elif period == 'este_mes':
        start_date = today.replace(day=1)
        group_by = 'day'
        title = 'Este Mês'
        today = today  # Até hoje
    elif period == 'mes_passado':
        # Primeiro dia do mês passado
        first_of_current_month = today.replace(day=1)
        last_month = first_of_current_month - timedelta(days=1)
        start_date = last_month.replace(day=1)
        today = first_of_current_month - timedelta(days=1)  # Último dia do mês passado
        group_by = 'day'
        title = f'{last_month.strftime("%B de %Y")}'
    elif period == 'ultimos_2meses':
        start_date = today - timedelta(days=60)
        group_by = 'week'
        title = 'Últimos 2 Meses'
    
    # Períodos por ano
    elif period == 'este_ano':
        start_date = today.replace(month=1, day=1)
        group_by = 'month'
        title = f'Este Ano ({today.year})'
    elif period == 'ano_passado':
        start_date = today.replace(year=today.year-1, month=1, day=1)
        today = today.replace(year=today.year-1, month=12, day=31)
        group_by = 'month'
        title = f'Ano Passado ({today.year})'
    elif period == 'ultimos_2anos':
        start_date = today - timedelta(days=730)
        group_by = 'month'
        title = 'Últimos 2 Anos'
    elif period == 'ultimos_5anos':
        start_date = today - timedelta(days=1825)
        group_by = 'month'
        title = 'Últimos 5 Anos'
    
    # Trimestres
    elif period == 'q1':  # Jan-Mar
        start_date = today.replace(month=1, day=1)
        today = today.replace(month=3, day=31) if today.month > 3 else today
        group_by = 'month'
        title = '1º Trimestre (Jan-Mar)'
    elif period == 'q2':  # Abr-Jun
        start_date = today.replace(month=4, day=1)
        today = today.replace(month=6, day=30) if today.month > 6 else today
        group_by = 'month'
        title = '2º Trimestre (Abr-Jun)'
    elif period == 'q3':  # Jul-Set
        start_date = today.replace(month=7, day=1)
        today = today.replace(month=9, day=30) if today.month > 9 else today
        group_by = 'month'
        title = '3º Trimestre (Jul-Set)'
    elif period == 'q4':  # Out-Dez
        start_date = today.replace(month=10, day=1)
        today = today.replace(month=12, day=31)
        group_by = 'month'
        title = '4º Trimestre (Out-Dez)'
    
    # Período personalizado
    elif period == 'custom':
        # Período personalizado
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if not start_date_str or not end_date_str:
            return JsonResponse({
                'labels': [],
                'entradas': [],
                'saidas': [],
                'title': 'Período inválido',
                'error': 'Datas não fornecidas'
            })
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'labels': [],
                'entradas': [],
                'saidas': [],
                'title': 'Período inválido',
                'error': 'Formato de data inválido'
            })
        
        # Definir agrupamento baseado no período
        days_diff = (end_date - start_date).days
        if days_diff <= 31:
            group_by = 'day'
        elif days_diff <= 180:
            group_by = 'week'
        else:
            group_by = 'month'
        
        title = f"{start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')}"
        today = end_date  # Usar end_date como limite superior
    else:
        start_date = today - timedelta(days=7)
        group_by = 'day'
        title = 'Últimos 7 Dias'
    
    # Iniciar query de movimentações com período
    movements_query = InventoryMovement.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=today
    )
    
    # Aplicar filtros avançados
    # Filtro de tipo de movimentação
    movement_types = request.GET.get('movement_type', '')
    if movement_types:
        type_list = [t.strip() for t in movement_types.split(',')]
        movements_query = movements_query.filter(type__in=type_list)
    
    # Filtro de produto
    product_id = request.GET.get('product_id')
    if product_id:
        movements_query = movements_query.filter(product_id=product_id)
    
    # Filtro de categoria
    category_id = request.GET.get('category_id')
    if category_id:
        movements_query = movements_query.filter(product__category_id=category_id)
    
    # Filtro de usuário
    user_id = request.GET.get('user_id')
    if user_id:
        movements_query = movements_query.filter(user_id=user_id)
    
    # Busca por texto (produto, SKU, documento, notas)
    search = request.GET.get('search')
    if search:
        from django.db.models import Q
        movements_query = movements_query.filter(
            Q(product__name__icontains=search) |
            Q(product__sku__icontains=search) |
            Q(document__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Filtro de quantidade
    min_quantity = request.GET.get('min_quantity')
    if min_quantity:
        try:
            movements_query = movements_query.filter(quantity__gte=Decimal(min_quantity))
        except (ValueError, TypeError):
            pass
    
    max_quantity = request.GET.get('max_quantity')
    if max_quantity:
        try:
            movements_query = movements_query.filter(quantity__lte=Decimal(max_quantity))
        except (ValueError, TypeError):
            pass
    
    # Buscar movimentações com agregação
    movements = movements_query.values('created_at__date', 'type').annotate(
        total=Count('id')
    ).order_by('created_at__date')
    
    # Organizar dados por agrupamento
    grouped_data = defaultdict(lambda: {'ENTRADA': 0, 'SAIDA': 0})
    
    for movement in movements:
        date = movement['created_at__date']
        mov_type = movement['type']
        total = movement['total']
        
        # Ignorar tipos que não sejam ENTRADA ou SAIDA
        if mov_type not in ['ENTRADA', 'SAIDA']:
            continue
        
        if group_by == 'day':
            key = date
        elif group_by == 'week':
            # Agrupar por semana (início da semana)
            days_since_monday = date.weekday()
            week_start = date - timedelta(days=days_since_monday)
            key = week_start
        elif group_by == 'month':
            # Agrupar por mês
            key = date.replace(day=1)
        
        grouped_data[key][mov_type] += total
    
    # Preencher gaps (datas sem movimentações)
    all_keys = set()
    current = start_date
    
    while current <= today:
        if group_by == 'day':
            all_keys.add(current)
            current += timedelta(days=1)
        elif group_by == 'week':
            days_since_monday = current.weekday()
            week_start = current - timedelta(days=days_since_monday)
            all_keys.add(week_start)
            current += timedelta(days=7)
        elif group_by == 'month':
            all_keys.add(current.replace(day=1))
            # Próximo mês
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
    
    # Garantir que todas as chaves tenham dados
    for key in all_keys:
        if key not in grouped_data:
            grouped_data[key] = {'ENTRADA': 0, 'SAIDA': 0}
    
    # Ordenar e formatar labels
    sorted_keys = sorted(grouped_data.keys())
    
    # Mapear mês em português
    month_names_full = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    month_names_short = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    
    # Verificar se há múltiplos anos nos dados
    years_in_data = {k.year for k in sorted_keys}
    multiple_years = len(years_in_data) > 1
    
    labels = []
    for key in sorted_keys:
        if group_by == 'day':
            # Formato: dd/mm
            labels.append(key.strftime('%d/%m'))
        elif group_by == 'week':
            # Formato: Semana dd/mm
            labels.append(f"Sem {key.strftime('%d/%m')}")
        elif group_by == 'month':
            # Formato: Nome do Mês ou Mês/Ano (se múltiplos anos)
            month_name = month_names_full[key.month]
            if multiple_years:
                labels.append(f"{month_names_short[key.month]}/{key.year}")
            else:
                labels.append(month_name)
    
    entradas = [grouped_data[key]['ENTRADA'] for key in sorted_keys]
    saidas = [grouped_data[key]['SAIDA'] for key in sorted_keys]
    
    return JsonResponse({
        'labels': labels,
        'entradas': entradas,
        'saidas': saidas,
        'title': title,
        'period': period,
    })
