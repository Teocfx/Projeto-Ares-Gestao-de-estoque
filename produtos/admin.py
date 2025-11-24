"""
Admin interface para o app produtos.
Configurações personalizadas para gerenciamento de produtos, categorias e unidades.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Product, Category, Unit


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para categorias de produtos."""
    
    list_display = ('name', 'description', 'product_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Conta quantos produtos ativos estão nesta categoria."""
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:produtos_product_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} produto{}</a>', url, count, 's' if count != 1 else '')
        return '0 produtos'
    product_count.short_description = 'Produtos'


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin para unidades de medida."""
    
    list_display = ('name', 'description', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_count(self, obj):
        """Conta quantos produtos ativos usam esta unidade."""
        count = obj.products.filter(is_active=True).count()
        if count > 0:
            url = reverse('admin:produtos_product_changelist') + f'?unit__id__exact={obj.id}'
            return format_html('<a href="{}">{} produto{}</a>', url, count, 's' if count != 1 else '')
        return '0 produtos'
    product_count.short_description = 'Produtos'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin para produtos."""
    
    list_display = (
        'sku', 'name', 'category', 'unit', 
        'current_stock', 'min_stock', 'stock_status_colored',
        'unit_price', 'total_value_display', 'expiry_status_display',
        'is_active'
    )
    
    list_filter = (
        'category', 'unit', 'is_active',
        ('expiry_date', admin.DateFieldListFilter),
        ('created_at', admin.DateFieldListFilter),
    )
    
    search_fields = ('sku', 'name', 'description', 'ncm')
    
    readonly_fields = ('created_at', 'updated_at', 'total_value')
    
    list_editable = ('current_stock', 'min_stock', 'unit_price', 'is_active')
    
    list_per_page = 25
    
    fieldsets = (
        ('Identificação', {
            'fields': ('sku', 'name', 'description', 'category', 'unit')
        }),
        ('Estoque', {
            'fields': ('current_stock', 'min_stock')
        }),
        ('Financeiro', {
            'fields': ('unit_price', 'total_value'),
            'classes': ('collapse',)
        }),
        ('Validade', {
            'fields': ('expiry_date',),
            'classes': ('collapse',)
        }),
        ('Dados Fiscais', {
            'fields': ('ncm',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_products', 'deactivate_products', 'reset_stock']
    
    def stock_status_colored(self, obj):
        """Exibe o status do estoque com cores."""
        status = obj.stock_status
        colors = {
            'CRITICO': '#dc3545',  # Vermelho
            'BAIXO': '#ffc107',    # Amarelo
            'OK': '#198754'        # Verde
        }
        color = colors.get(status, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.stock_status_display
        )
    stock_status_colored.short_description = 'Status Estoque'
    stock_status_colored.admin_order_field = 'current_stock'
    
    def total_value_display(self, obj):
        """Exibe o valor total formatado."""
        if obj.total_value:
            return format_html('R$ {:.2f}', obj.total_value)
        return '-'
    total_value_display.short_description = 'Valor Total'
    total_value_display.admin_order_field = 'unit_price'
    
    def expiry_status_display(self, obj):
        """Exibe o status de validade com cores."""
        status = obj.expiry_status
        if not status:
            return '-'
        
        colors = {
            'VENCIDO': '#dc3545',   # Vermelho
            'PROXIMO': '#ffc107',   # Amarelo
            'OK': '#198754'         # Verde
        }
        
        status_text = {
            'VENCIDO': '🔴 Vencido',
            'PROXIMO': '🟡 Próximo',
            'OK': '🟢 OK'
        }
        
        color = colors.get(status, '#6c757d')
        text = status_text.get(status, status)
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            text
        )
    expiry_status_display.short_description = 'Validade'
    expiry_status_display.admin_order_field = 'expiry_date'
    
    def activate_products(self, request, queryset):
        """Ativa os produtos selecionados."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} produto(s) ativado(s) com sucesso.')
    activate_products.short_description = 'Ativar produtos selecionados'
    
    def deactivate_products(self, request, queryset):
        """Desativa os produtos selecionados."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} produto(s) desativado(s) com sucesso.')
    deactivate_products.short_description = 'Desativar produtos selecionados'
    
    def reset_stock(self, request, queryset):
        """Zera o estoque dos produtos selecionados."""
        updated = queryset.update(current_stock=0)
        self.message_user(request, f'Estoque zerado para {updated} produto(s).')
    reset_stock.short_description = 'Zerar estoque dos produtos selecionados'
