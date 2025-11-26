"""
Views para sistema de relatórios.
Geração de relatórios com filtros avançados e exportação.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.http import JsonResponse, HttpResponse, Http404
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import json

from .models import ReportGeneration, ReportType, ReportTemplate
from produtos.models import Product, Category
from movimentacoes.models import InventoryMovement
from .forms import ReportFilterForm, ReportGenerationForm
from .pdf_generator import PDFGenerator, ReportExporter


class ReportIndexView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Página principal de relatórios com resumo e links."""
    
    template_name = 'relatorios/index.html'
    context_object_name = 'recent_reports'
    model = ReportGeneration
    paginate_by = 10
    permission_required = 'relatorios.view_report'
    permission_denied_message = 'Você não tem permissão para visualizar relatórios.'
    
    def get_queryset(self):
        return ReportGeneration.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas gerais
        context.update({
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_products': Product.objects.filter(
                is_active=True,
                current_stock__lte=F('min_stock')
            ).count(),
            'recent_movements': InventoryMovement.objects.count(),
            'report_types': ReportType.objects.filter(is_active=True),
        })
        
        return context


@login_required
def index(request):
    """View funcional - redireciona para CBV."""
    view = ReportIndexView.as_view()
    return view(request)


@login_required
@permission_required('relatorios.add_reportgeneration', raise_exception=True)
def generate_report(request):
    """Página para gerar novo relatório."""
    
    if request.method == 'POST':
        form = ReportGenerationForm(request.POST)
        if form.is_valid():
            try:
                # Criar registro de geração
                report = form.save(commit=False)
                report.user = request.user
                report.status = ReportGeneration.STATUS_PROCESSING
                report.save()
                
                # Processar relatório (aqui seria async em produção)
                success = process_report(report)
                
                if success:
                    messages.success(
                        request, 
                        'Relatório gerado com sucesso! Você pode fazer o download abaixo.'
                    )
                    return redirect('relatorios:detail', pk=report.pk)
                else:
                    messages.error(request, 'Erro ao gerar relatório. Tente novamente.')
                    
            except Exception as e:
                messages.error(request, f'Erro: {str(e)}')
                
    else:
        form = ReportGenerationForm()
    
    # Tipos de relatório
    report_types_data = [
        {
            'id': 'estoque',
            'name': 'Relatório de Estoque',
            'description': 'Estoque atual de todos os produtos',
            'icon': 'boxes'
        },
        {
            'id': 'movimentacoes',
            'name': 'Relatório de Movimentações',
            'description': 'Histórico de entradas e saídas',
            'icon': 'arrow-left-right'
        },
        {
            'id': 'vencimentos',
            'name': 'Relatório de Vencimentos',
            'description': 'Produtos próximos ao vencimento',
            'icon': 'calendar-x'
        },
        {
            'id': 'financeiro',
            'name': 'Relatório Financeiro',
            'description': 'Valor total do estoque por categoria',
            'icon': 'currency-dollar'
        },
    ]
    
    context = {
        'form': form,
        'report_types': report_types_data,
        'categories': Category.objects.filter(is_active=True),
    }
    return render(request, 'relatorios/generate.html', context)


@login_required
@permission_required('relatorios.view_reportgeneration', raise_exception=True)
def report_detail(request, pk):
    """Detalhes de um relatório gerado."""
    report = get_object_or_404(ReportGeneration, pk=pk, user=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'relatorios/detail.html', context)


@login_required
@permission_required('relatorios.view_reportgeneration', raise_exception=True)
def download_report(request, pk):
    """Download de arquivo de relatório."""
    report = get_object_or_404(ReportGeneration, pk=pk, user=request.user)
    
    if not report.is_ready:
        raise Http404("Relatório não está pronto para download")
    
    try:
        # Em produção, seria servido pelo nginx/apache
        # Aqui é uma implementação simplificada
        response = HttpResponse(
            content_type='application/pdf' if report.format == 'pdf' else 'application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{report.title}.{report.format}"'
        response.write(b'Conteudo do relatorio aqui...')  # Placeholder
        
        return response
        
    except Exception as e:
        messages.error(request, f'Erro ao fazer download: {str(e)}')
        return redirect('relatorios:detail', pk=pk)


# Relatórios específicos por tipo
@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def relatorio_estoque(request):
    """Relatório de estoque atual."""
    
    # Filtros
    search = request.GET.get('search', '')
    category_id = request.GET.get('category')
    status = request.GET.get('status')
    
    # Queryset base
    products = Product.objects.filter(is_active=True).select_related('category', 'unit')
    
    # Aplicar filtros
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(sku__icontains=search)
        )
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if status:
        if status == 'critico':
            products = products.filter(current_stock=0)
        elif status == 'baixo':
            products = products.filter(
                current_stock__gt=0,
                current_stock__lte=F('min_stock')
            )
        elif status == 'ok':
            products = products.filter(current_stock__gt=F('min_stock'))
    
    # Estatísticas
    # Calcular valor total (current_stock * unit_price)
    total_value = 0
    for p in products:
        unit_price = getattr(p, 'unit_price', None) or 0
        total_value += float(p.current_stock) * float(unit_price)
    
    stats = {
        'total_products': products.count(),
        'total_value': total_value,
        'critical_count': products.filter(current_stock=0).count(),
        'low_count': products.filter(
            current_stock__gt=0,
            current_stock__lte=F('min_stock')
        ).count(),
    }
    
    # Paginação
    paginator = Paginator(products.order_by('name'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'stats': stats,
        'current_filters': {
            'search': search,
            'category': category_id,
            'status': status,
        },
    }
    return render(request, 'relatorios/estoque.html', context)


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def relatorio_movimentacoes(request):
    """Relatório de movimentações por período."""
    
    # Parâmetros de período
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    movement_type = request.GET.get('type')
    product_id = request.GET.get('product')
    
    # Período padrão (últimos 30 dias)
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Queryset
    movements = InventoryMovement.objects.filter(
        created_at__date__range=[date_from, date_to]
    ).select_related('product', 'user')
    
    # Filtros adicionais
    if movement_type:
        movements = movements.filter(type=movement_type)
    
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    # Estatísticas
    stats = {
        'total_movements': movements.count(),
        'entradas': movements.filter(type=InventoryMovement.ENTRADA).count(),
        'saidas': movements.filter(type=InventoryMovement.SAIDA).count(),
        'ajustes': movements.filter(type=InventoryMovement.AJUSTE).count(),
    }
    
    # Paginação
    paginator = Paginator(movements.order_by('-created_at'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'movements': page_obj,
        'stats': stats,
        'movement_types': InventoryMovement.TYPE_CHOICES,
        'products': Product.objects.filter(is_active=True).order_by('name'),
        'current_filters': {
            'date_from': date_from.strftime('%Y-%m-%d'),
            'date_to': date_to.strftime('%Y-%m-%d'),
            'type': movement_type,
            'product': product_id,
        },
    }
    return render(request, 'relatorios/movimentacoes.html', context)


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def relatorio_vencimentos(request):
    """Relatório de produtos próximos ao vencimento."""
    
    # Parâmetros
    days_ahead = int(request.GET.get('days', 30))
    include_expired = request.GET.get('expired', 'true') == 'true'
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    # Produtos com data de vencimento
    products = Product.objects.filter(
        is_active=True,
        expiry_date__isnull=False
    ).select_related('category', 'unit')
    
    # Filtrar por período
    if include_expired:
        products = products.filter(expiry_date__lte=future_date)
    else:
        products = products.filter(
            expiry_date__gte=today,
            expiry_date__lte=future_date
        )
    
    # Categorizar por urgência
    expired = products.filter(expiry_date__lt=today)
    critical = products.filter(expiry_date__range=[today, today + timedelta(days=7)])
    warning = products.filter(expiry_date__range=[today + timedelta(days=8), today + timedelta(days=30)])
    
    context = {
        'products': products.order_by('expiry_date'),
        'expired': expired,
        'critical': critical,
        'warning': warning,
        'days_ahead': days_ahead,
        'include_expired': include_expired,
        'stats': {
            'total': products.count(),
            'expired_count': expired.count(),
            'critical_count': critical.count(),
            'warning_count': warning.count(),
        }
    }
    return render(request, 'relatorios/vencimentos.html', context)


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def relatorio_financeiro(request):
    """Relatório financeiro - valor do estoque por categoria."""
    
    # Filtros
    category_id = request.GET.get('category')
    
    # Buscar produtos ativos
    products = Product.objects.filter(is_active=True).select_related('category', 'unit')
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Agrupar por categoria e calcular totais
    categories_data = []
    categories = Category.objects.filter(is_active=True)
    
    total_general = 0
    total_products = 0
    
    for category in categories:
        category_products = products.filter(category=category)
        category_total = 0
        
        for product in category_products:
            unit_price = getattr(product, 'unit_price', None) or 0
            product_total = float(product.current_stock) * float(unit_price)
            category_total += product_total
        
        if category_products.exists():
            categories_data.append({
                'category': category,
                'products_count': category_products.count(),
                'total_value': category_total,
                'products': category_products
            })
            
            total_general += category_total
            total_products += category_products.count()
    
    # Ordenar por valor total (maior primeiro)
    categories_data.sort(key=lambda x: x['total_value'], reverse=True)
    
    context = {
        'categories_data': categories_data,
        'categories': categories,
        'stats': {
            'total_value': total_general,
            'total_products': total_products,
            'total_categories': len(categories_data),
        },
        'current_filters': {
            'category': category_id,
        }
    }
    return render(request, 'relatorios/financeiro.html', context)


@login_required
@permission_required('relatorios.add_reportgeneration', raise_exception=True)
def generate_custom_report(request):
    """Gerar relatório personalizado simplificado."""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        title = request.POST.get('title', f'Relatório {report_type}')
        format_type = request.POST.get('format', 'pdf')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        categories = request.POST.get('categories', '')
        include_inactive = request.POST.get('include_inactive') == 'on'
        
        # Construir query params para passar aos relatórios
        params = []
        if date_from:
            params.append(f'date_from={date_from}')
        if date_to:
            params.append(f'date_to={date_to}')
        if categories:
            # Pegar primeira categoria para simplificar
            first_category = categories.split(',')[0] if categories else None
            if first_category:
                params.append(f'category={first_category}')
        if include_inactive:
            params.append('include_inactive=true')
        
        query_string = '&'.join(params) if params else ''
        
        # Redirecionar para o relatório correto com parâmetros
        if report_type == 'estoque':
            messages.success(request, f'Gerando relatório: {title}')
            if query_string:
                return redirect(f'/relatorios/estoque/?{query_string}')
            return redirect('relatorios:estoque')
        elif report_type == 'movimentacoes':
            messages.success(request, f'Gerando relatório: {title}')
            if query_string:
                return redirect(f'/relatorios/movimentacoes/?{query_string}')
            return redirect('relatorios:movimentacoes')
        elif report_type == 'vencimentos':
            messages.success(request, f'Gerando relatório: {title}')
            if query_string:
                return redirect(f'/relatorios/vencimentos/?{query_string}')
            return redirect('relatorios:vencimentos')
        elif report_type == 'financeiro':
            messages.success(request, f'Gerando relatório financeiro: {title}')
            if query_string:
                return redirect(f'/relatorios/financeiro/?{query_string}')
            return redirect('relatorios:financeiro')
        else:
            messages.warning(request, 'Tipo de relatório não selecionado')
            return redirect('relatorios:generate')
    
    return redirect('relatorios:generate')


# ====== FUNÇÕES DE DOWNLOAD DE PDF ======

@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def download_estoque_pdf(request):
    """Download do relatório de estoque em PDF."""
    try:
        # Obter mesmos filtros da view
        search = request.GET.get('search', '')
        category_id = request.GET.get('category')
        status = request.GET.get('status')
        
        products = Product.objects.filter(is_active=True).select_related('category', 'unit')
        
        if search:
            products = products.filter(Q(name__icontains=search) | Q(sku__icontains=search))
        if category_id:
            products = products.filter(category_id=category_id)
        if status:
            if status == 'critico':
                products = products.filter(current_stock=0)
            elif status == 'baixo':
                products = products.filter(current_stock__gt=0, current_stock__lte=F('min_stock'))
            elif status == 'ok':
                products = products.filter(current_stock__gt=F('min_stock'))
        
        # Estatísticas
        total_value = sum(float(p.current_stock) * float(getattr(p, 'unit_price', 0) or 0) for p in products)
        total_products = products.count()
        critical_count = products.filter(current_stock=0).count()
        low_count = products.filter(current_stock__gt=0, current_stock__lte=F('min_stock')).count()
        ok_count = total_products - critical_count - low_count
        
        stats = {
            'total_products': total_products,
            'total_value': total_value,
            'critical_count': critical_count,
            'low_count': low_count,
            'ok_count': ok_count,
        }
        
        # Gerar PDF
        pdf_gen = PDFGenerator(
            title="Relatório de Estoque",
            subtitle="Situação atual do estoque de produtos",
            author=request.user.get_full_name() or request.user.username
        )
        
        context = {
            'products': products.order_by('name')[:500],  # Limitar para performance
            'stats': stats,
        }
        
        pdf_content = pdf_gen.generate_pdf('relatorios/pdf/estoque.html', context)
        
        # Sempre retornar como PDF para download
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="relatorio_estoque_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response
            
    except Exception as e:
        # Se falhar, redirecionar com mensagem
        messages.error(request, f'Erro ao gerar PDF: {str(e)}. Tente exportar em outro formato.')
        return redirect('relatorios:estoque')


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def download_movimentacoes_pdf(request):
    """Download do relatório de movimentações em PDF."""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    movement_type = request.GET.get('type')
    product_id = request.GET.get('product')
    
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Query base com filtros de data
    movements_base = InventoryMovement.objects.filter(
        created_at__date__range=[date_from, date_to]
    ).select_related('product', 'user')
    
    # Aplicar filtros adicionais
    movements = movements_base
    if movement_type:
        movements = movements.filter(type=movement_type)
    if product_id:
        movements = movements.filter(product_id=product_id)
    
    # Estatísticas respeitando os filtros aplicados
    stats = {
        'total_movements': movements.count(),
        'entradas': movements.filter(type=InventoryMovement.ENTRADA).count(),
        'saidas': movements.filter(type=InventoryMovement.SAIDA).count(),
        'ajustes': movements.filter(type=InventoryMovement.AJUSTE).count(),
    }
    
    pdf_gen = PDFGenerator(
        title="Relatório de Movimentações",
        subtitle=f"Período: {date_from.strftime('%d/%m/%Y')} a {date_to.strftime('%d/%m/%Y')}",
        author=request.user.get_full_name() or request.user.username
    )
    
    context = {
        'movements': movements.order_by('-created_at')[:500],
        'stats': stats,
        'current_filters': {
            'date_from': date_from.strftime('%d/%m/%Y'),
            'date_to': date_to.strftime('%d/%m/%Y'),
        }
    }
    
    pdf_bytes = pdf_gen.generate_pdf('relatorios/pdf/movimentacoes.html', context)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_movimentacoes_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def download_vencimentos_pdf(request):
    """Download do relatório de vencimentos em PDF."""
    days_ahead = int(request.GET.get('days', 30))
    include_expired = request.GET.get('expired', 'true') == 'true'
    
    today = timezone.now().date()
    future_date = today + timedelta(days=days_ahead)
    
    # Query base - produtos com data de validade
    products_base = Product.objects.filter(is_active=True, expiry_date__isnull=False).select_related('category', 'unit')
    
    # Aplicar filtro de período
    if include_expired:
        products = products_base.filter(expiry_date__lte=future_date)
    else:
        products = products_base.filter(expiry_date__gte=today, expiry_date__lte=future_date)
    
    # Calcular estatísticas baseadas nos produtos filtrados
    expired = products.filter(expiry_date__lt=today)
    critical = products.filter(expiry_date__range=[today, today + timedelta(days=7)])
    warning = products.filter(expiry_date__range=[today + timedelta(days=8), future_date])
    
    pdf_gen = PDFGenerator(
        title="Relatório de Vencimentos",
        subtitle=f"Produtos vencidos e próximos ao vencimento ({days_ahead} dias)",
        author=request.user.get_full_name() or request.user.username
    )
    
    context = {
        'expiring_products': products.order_by('expiry_date'),
        'expired': expired,
        'critical': critical,
        'warning': warning,
        'stats': {
            'total': products.count(),
            'expired_count': expired.count(),
            'critical_count': critical.count(),
            'warning_count': warning.count(),
        }
    }
    
    pdf_bytes = pdf_gen.generate_pdf('relatorios/pdf/vencimentos.html', context)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_vencimentos_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


@login_required
@permission_required('relatorios.view_report', raise_exception=True)
def download_financeiro_pdf(request):
    """Download do relatório financeiro em PDF."""
    category_id = request.GET.get('category')
    
    products = Product.objects.filter(is_active=True).select_related('category', 'unit')
    if category_id:
        products = products.filter(category_id=category_id)
    
    categories_data = []
    categories = Category.objects.filter(is_active=True)
    total_general = 0
    total_products = 0
    
    for category in categories:
        category_products = products.filter(category=category)
        category_total = sum(
            float(p.current_stock) * float(getattr(p, 'unit_price', 0) or 0)
            for p in category_products
        )
        
        if category_products.exists():
            categories_data.append({
                'category': category,
                'products_count': category_products.count(),
                'total_value': category_total,
                'products': category_products
            })
            total_general += category_total
            total_products += category_products.count()
    
    categories_data.sort(key=lambda x: x['total_value'], reverse=True)
    
    pdf_gen = PDFGenerator(
        title="Relatório Financeiro",
        subtitle="Valor do estoque por categoria",
        author=request.user.get_full_name() or request.user.username
    )
    
    context = {
        'categories_data': categories_data,
        'stats': {
            'total_value': total_general,
            'total_products': total_products,
            'total_categories': len(categories_data),
        }
    }
    
    pdf_bytes = pdf_gen.generate_pdf('relatorios/pdf/financeiro.html', context)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    return response


# Função auxiliar para processamento de relatórios
def process_report(report):
    """
    Processa a geração de um relatório.
    Em produção seria uma task assíncrona (Celery).
    """
    try:
        start_time = timezone.now()
        
        # Simular processamento
        import time
        time.sleep(1)  # Simular tempo de processamento
        
        # Atualizar status
        report.status = ReportGeneration.STATUS_COMPLETED
        report.processing_time = timezone.now() - start_time
        report.file_path = f"/tmp/report_{report.pk}.pdf"
        report.file_size = 1024 * 50  # 50KB simulado
        report.total_records = 100  # Simulado
        report.save()
        
        return True
        
    except Exception as e:
        report.status = ReportGeneration.STATUS_ERROR
        report.error_message = str(e)
        report.save()
        return False
