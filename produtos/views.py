"""
Views para o app produtos.
Views baseadas em classe com CRUD completo e funcionalidades avançadas.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, F
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from decimal import Decimal
import json

from .models import Product, Category, Unit
from .forms import (
    ProductForm, CategoryForm, UnitForm, 
    ProductSearchForm, ProductBulkActionForm
)

# Constantes para URLs
PRODUCT_LIST_URL = 'produtos:list'
CATEGORY_LIST_URL = 'produtos:category_list'
UNIT_LIST_URL = 'produtos:unit_list'


class ProductListView(LoginRequiredMixin, ListView):
    """Lista de produtos com busca, filtros e paginação."""
    
    model = Product
    template_name = 'produtos/product_list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        """Filtrar produtos baseado nos parâmetros de busca."""
        queryset = Product.objects.select_related('category', 'unit').all()
        
        # Busca por texto
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(sku__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filtro por categoria
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filtro por unidade
        unit = self.request.GET.get('unit')
        if unit:
            queryset = queryset.filter(unit_id=unit)
        
        # Filtro por status do estoque
        stock_status = self.request.GET.get('stock_status')
        if stock_status == 'CRITICO':
            queryset = queryset.filter(current_stock=0)
        elif stock_status == 'BAIXO':
            queryset = queryset.filter(
                current_stock__gt=0,
                current_stock__lte=F('min_stock')
            )
        elif stock_status == 'OK':
            queryset = queryset.filter(current_stock__gt=F('min_stock'))
        
        # Filtro por status ativo/inativo
        active = self.request.GET.get('active')
        if active == '1':
            queryset = queryset.filter(is_active=True)
        elif active == '0':
            queryset = queryset.filter(is_active=False)
        
        # Ordenação
        order_by = self.request.GET.get('order_by', 'name')
        if order_by in ['sku', 'name', 'category__name', 'current_stock', 'created_at']:
            direction = self.request.GET.get('direction', 'asc')
            if direction == 'desc':
                order_by = f'-{order_by}'
            queryset = queryset.order_by(order_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Adicionar formulário de busca e estatísticas ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Formulário de busca com dados atuais
        context['search_form'] = ProductSearchForm(self.request.GET)
        
        # Estatísticas da busca atual
        total_products = self.get_queryset().count()
        total_stock_value = self.get_queryset().aggregate(
            total_value=Sum(F('current_stock') * F('unit_price'))
        )['total_value'] or Decimal('0')
        
        context['stats'] = {
            'total_products': total_products,
            'total_stock_value': total_stock_value,
            'critical_stock': self.get_queryset().filter(current_stock=0).count(),
            'low_stock': self.get_queryset().filter(
                current_stock__gt=0,
                current_stock__lte=F('min_stock')
            ).count(),
        }
        
        # Parâmetros de ordenação para o template
        context['current_order'] = self.request.GET.get('order_by', 'name')
        context['current_direction'] = self.request.GET.get('direction', 'asc')
        
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    """Detalhes de um produto específico."""
    
    model = Product
    template_name = 'produtos/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        """Adicionar informações extras ao contexto."""
        context = super().get_context_data(**kwargs)
        
        # Histórico de movimentações (se o app já estiver implementado)
        # context['recent_movements'] = self.object.movements.all()[:10]
        
        return context


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Criar novo produto."""
    
    model = Product
    form_class = ProductForm
    template_name = 'produtos/product_form.html'
    success_url = reverse_lazy(PRODUCT_LIST_URL)
    permission_required = 'produtos.add_product'
    
    def form_valid(self, form):
        """Processar formulário válido."""
        messages.success(self.request, f'Produto "{form.instance.name}" criado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Adicionar título ao contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Produto'
        context['action'] = 'create'
        return context


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar produto existente."""
    
    model = Product
    form_class = ProductForm
    template_name = 'produtos/product_form.html'
    success_url = reverse_lazy(PRODUCT_LIST_URL)
    permission_required = 'produtos.change_product'
    
    def form_valid(self, form):
        """Processar formulário válido."""
        messages.success(self.request, f'Produto "{form.instance.name}" atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        """Adicionar título ao contexto."""
        context = super().get_context_data(**kwargs)
        context['title'] = f'Editar Produto: {self.object.name}'
        context['action'] = 'update'
        return context


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Excluir produto."""
    
    model = Product
    template_name = 'produtos/product_confirm_delete.html'
    success_url = reverse_lazy(PRODUCT_LIST_URL)
    permission_required = 'produtos.delete_product'
    
    def delete(self, request, *args, **kwargs):
        """Processar exclusão com mensagem."""
        product_name = self.get_object().name
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Produto "{product_name}" excluído com sucesso!')
        return result


# Views para Categorias
class CategoryListView(LoginRequiredMixin, ListView):
    """Lista de categorias."""
    
    model = Category
    template_name = 'produtos/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    
    def get_queryset(self):
        """Ordenar categorias por nome e incluir contagem de produtos."""
        return Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Criar nova categoria."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'produtos/category_form.html'
    success_url = reverse_lazy(CATEGORY_LIST_URL)
    permission_required = 'produtos.add_category'
    
    def form_valid(self, form):
        messages.success(self.request, f'Categoria "{form.instance.name}" criada com sucesso!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar categoria."""
    
    model = Category
    form_class = CategoryForm
    template_name = 'produtos/category_form.html'
    success_url = reverse_lazy(CATEGORY_LIST_URL)
    permission_required = 'produtos.change_category'
    
    def form_valid(self, form):
        messages.success(self.request, f'Categoria "{form.instance.name}" atualizada com sucesso!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Excluir categoria."""
    
    model = Category
    template_name = 'produtos/category_confirm_delete.html'
    success_url = reverse_lazy(CATEGORY_LIST_URL)
    permission_required = 'produtos.delete_category'
    
    def delete(self, request, *args, **kwargs):
        category_name = self.get_object().name
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Categoria "{category_name}" excluída com sucesso!')
        return result


# Views para Unidades
class UnitListView(LoginRequiredMixin, ListView):
    """Lista de unidades."""
    
    model = Unit
    template_name = 'produtos/unit_list.html'
    context_object_name = 'units'
    paginate_by = 20
    
    def get_queryset(self):
        """Ordenar unidades por nome e incluir contagem de produtos."""
        return Unit.objects.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('name')


class UnitCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Criar nova unidade."""
    
    model = Unit
    form_class = UnitForm
    template_name = 'produtos/unit_form.html'
    success_url = reverse_lazy(UNIT_LIST_URL)
    permission_required = 'produtos.add_unit'
    
    def form_valid(self, form):
        messages.success(self.request, f'Unidade "{form.instance.name}" criada com sucesso!')
        return super().form_valid(form)


class UnitUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Editar unidade."""
    
    model = Unit
    form_class = UnitForm
    template_name = 'produtos/unit_form.html'
    success_url = reverse_lazy(UNIT_LIST_URL)
    permission_required = 'produtos.change_unit'
    
    def form_valid(self, form):
        messages.success(self.request, f'Unidade "{form.instance.name}" atualizada com sucesso!')
        return super().form_valid(form)


class UnitDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Excluir unidade."""
    
    model = Unit
    template_name = 'produtos/unit_confirm_delete.html'
    success_url = reverse_lazy(UNIT_LIST_URL)
    permission_required = 'produtos.delete_unit'
    
    def delete(self, request, *args, **kwargs):
        unit_name = self.get_object().name
        result = super().delete(request, *args, **kwargs)
        messages.success(request, f'Unidade "{unit_name}" excluída com sucesso!')
        return result


# Views de API/AJAX
@method_decorator(login_required, name='dispatch')
class ProductBulkActionView(View):
    """Ações em lote para produtos (AJAX)."""
    
    def post(self, request):
        """Processar ações em lote."""
        form = ProductBulkActionForm(request.POST)
        
        if not form.is_valid():
            return JsonResponse({
                'success': False,
                'message': 'Dados inválidos.'
            })
        
        action = form.cleaned_data['action']
        product_ids = json.loads(form.cleaned_data['selected_products'])
        
        # Verificar permissões
        if not request.user.has_perm('produtos.change_product'):
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para esta ação.'
            })
        
        try:
            products = Product.objects.filter(id__in=product_ids)
            
            if action == 'activate':
                count = products.update(is_active=True)
                message = f'{count} produto(s) ativado(s) com sucesso.'
                
            elif action == 'deactivate':
                count = products.update(is_active=False)
                message = f'{count} produto(s) desativado(s) com sucesso.'
                
            elif action == 'update_min_stock':
                new_min_stock = form.cleaned_data['new_min_stock']
                count = products.update(min_stock=new_min_stock)
                message = f'Estoque mínimo atualizado para {count} produto(s).'
            
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Ação inválida.'
                })
            
            return JsonResponse({
                'success': True,
                'message': message,
                'count': count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao executar ação: {str(e)}'
            })


@login_required
def product_autocomplete(request):
    """API para autocomplete de produtos (AJAX)."""
    term = request.GET.get('term', '').strip()
    
    if len(term) < 2:
        return JsonResponse([], safe=False)
    
    products = Product.objects.filter(
        Q(sku__icontains=term) | Q(name__icontains=term),
        is_active=True
    ).values('id', 'sku', 'name', 'current_stock')[:20]
    
    results = [
        {
            'id': p['id'],
            'label': f"{p['sku']} - {p['name']}",
            'value': p['name'],
            'sku': p['sku'],
            'stock': float(p['current_stock'])
        }
        for p in products
    ]
    
    return JsonResponse(results, safe=False)


@login_required
def dashboard_products(request):
    """Dados de produtos para o dashboard (AJAX)."""
    # Estatísticas gerais
    total_products = Product.objects.filter(is_active=True).count()
    critical_stock = Product.objects.filter(
        is_active=True, 
        current_stock=0
    ).count()
    low_stock = Product.objects.filter(
        is_active=True,
        current_stock__gt=0,
        current_stock__lte=F('min_stock')
    ).count()
    
    # Valor total do estoque
    total_stock_value = Product.objects.filter(is_active=True).aggregate(
        total=Sum(F('current_stock') * F('unit_price'))
    )['total'] or Decimal('0')
    
    # Produtos com estoque crítico
    critical_products = Product.objects.filter(
        is_active=True,
        current_stock=0
    ).values('sku', 'name')[:10]
    
    # Produtos com estoque baixo
    low_stock_products = Product.objects.filter(
        is_active=True,
        current_stock__gt=0,
        current_stock__lte=F('min_stock')
    ).values('sku', 'name', 'current_stock', 'min_stock')[:10]
    
    return JsonResponse({
        'stats': {
            'total_products': total_products,
            'critical_stock': critical_stock,
            'low_stock': low_stock,
            'total_stock_value': float(total_stock_value)
        },
        'critical_products': list(critical_products),
        'low_stock_products': list(low_stock_products)
    })
