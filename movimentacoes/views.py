"""
Views para movimentações de estoque.
Sistema completo de CRUD com filtros e validações.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.db.models import Q, Sum, Count
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta

from .models import InventoryMovement
from produtos.models import Product
from .forms import InventoryMovementForm


class MovementListView(LoginRequiredMixin, ListView):
    """Lista paginada de movimentações com filtros avançados."""
    
    model = InventoryMovement
    template_name = 'movimentacoes/list.html'
    context_object_name = 'movements'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Aplicar filtros
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__name__icontains=search) |
                Q(product__sku__icontains=search) |
                Q(document__icontains=search) |
                Q(notes__icontains=search)
            )
        
        # Filtro por tipo
        movement_type = self.request.GET.get('type')
        if movement_type:
            queryset = queryset.filter(type=movement_type)
        
        # Filtro por produto
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Filtro por usuário
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtro por período
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to)
            except ValueError:
                pass
        
        return queryset.select_related('product', 'user', 'product__category', 'product__unit')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas do período filtrado
        movements = self.get_queryset()
        
        context.update({
            'total_movements': movements.count(),
            'entradas': movements.filter(type=InventoryMovement.ENTRADA).count(),
            'saidas': movements.filter(type=InventoryMovement.SAIDA).count(),
            'ajustes': movements.filter(type=InventoryMovement.AJUSTE).count(),
            
            # Para os filtros
            'products': Product.objects.filter(is_active=True).order_by('name'),
            'movement_types': InventoryMovement.TYPE_CHOICES,
            
            # Manter valores dos filtros
            'current_search': self.request.GET.get('search', ''),
            'current_type': self.request.GET.get('type', ''),
            'current_product': self.request.GET.get('product', ''),
            'current_date_from': self.request.GET.get('date_from', ''),
            'current_date_to': self.request.GET.get('date_to', ''),
        })
        
        return context


class MovementCreateView(LoginRequiredMixin, CreateView):
    """Criar nova movimentação de estoque."""
    
    model = InventoryMovement
    form_class = InventoryMovementForm
    template_name = 'movimentacoes/form.html'
    success_url = reverse_lazy('movimentacoes:list')

    def form_valid(self, form):
        try:
            # Define o usuário atual
            form.instance.user = self.request.user
            
            response = super().form_valid(form)
            
            messages.success(
                self.request,
                f'Movimentação registrada com sucesso! '
                f'Estoque atualizado: {form.instance.stock_after} {form.instance.product.unit}'
            )
            
            return response
            
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Nova Movimentação',
            'products': Product.objects.filter(is_active=True).order_by('name'),
            'submit_button_text': 'Salvar Movimentação',
            'cancel_url': reverse_lazy('movimentacoes:list'),
        })
        return context


class MovementDetailView(LoginRequiredMixin, DetailView):
    """Visualizar detalhes de uma movimentação."""
    
    model = InventoryMovement
    template_name = 'movimentacoes/detail.html'
    context_object_name = 'movement'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar movimentações relacionadas do mesmo produto
        related_movements = InventoryMovement.objects.filter(
            product=self.object.product
        ).exclude(pk=self.object.pk).order_by('-created_at')[:5]
        
        context.update({
            'related_movements': related_movements,
            'can_edit': self.request.user == self.object.user or self.request.user.is_superuser,
        })
        
        return context


# Views funcionais para compatibilidade com URLs existentes
@login_required
def list_movimentacoes(request):
    """View funcional - redireciona para CBV."""
    view = MovementListView.as_view()
    return view(request)


@login_required
def create_movimentacao(request):
    """View funcional - redireciona para CBV."""
    view = MovementCreateView.as_view()
    return view(request)


@login_required
def detail_movimentacao(request, pk):
    """View funcional - redireciona para CBV."""
    view = MovementDetailView.as_view()
    return view(request, pk=pk)


# API Views para AJAX
@login_required
def get_product_stock(request, product_id):
    """API para buscar estoque atual de um produto."""
    try:
        product = Product.objects.get(pk=product_id, is_active=True)
        return JsonResponse({
            'success': True,
            'current_stock': float(product.current_stock),
            'unit': product.unit.name,
            'min_stock': float(product.min_stock),
            'status': product.stock_status,
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Produto não encontrado'
        })


@login_required
def movement_statistics(request):
    """API para estatísticas de movimentações por período."""
    
    # Parâmetros de período
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Dados por dia
    movements = InventoryMovement.objects.filter(
        created_at__range=[start_date, end_date]
    )
    
    # Agrupar por tipo e contar
    stats = {
        'entradas': movements.filter(type=InventoryMovement.ENTRADA).count(),
        'saidas': movements.filter(type=InventoryMovement.SAIDA).count(),
        'ajustes': movements.filter(type=InventoryMovement.AJUSTE).count(),
        'total': movements.count(),
    }
    
    return JsonResponse(stats)
