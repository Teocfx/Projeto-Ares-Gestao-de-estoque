"""
Views para sistema de relatórios.
Geração de relatórios com filtros avançados e exportação.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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


class ReportIndexView(LoginRequiredMixin, ListView):
    """Página principal de relatórios com resumo e links."""
    
    template_name = 'relatorios/index.html'
    context_object_name = 'recent_reports'
    model = ReportGeneration
    paginate_by = 10
    
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
    
    context = {
        'form': form,
        'report_types': ReportType.objects.filter(is_active=True),
    }
    return render(request, 'relatorios/generate.html', context)


@login_required 
def report_detail(request, pk):
    """Detalhes de um relatório gerado."""
    report = get_object_or_404(ReportGeneration, pk=pk, user=request.user)
    
    context = {
        'report': report,
    }
    return render(request, 'relatorios/detail.html', context)


@login_required
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
    stats = {
        'total_products': products.count(),
        'total_value': sum(p.current_stock * getattr(p, 'price', 0) for p in products),
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
