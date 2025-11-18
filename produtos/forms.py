"""
Forms para o app produtos.
Formulários personalizados com validação e widgets responsivos.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import re
from .models import Product, Category, Unit

# Constante para evitar duplicação
DESCRICAO_LABEL = 'Descrição'


class CategoryForm(forms.ModelForm):
    """Formulário para categorias de produtos."""
    
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Alimentos, Eletrônicos, Limpeza',
                'maxlength': '100'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição detalhada da categoria (opcional)',
                'rows': 3
            })
        }
        labels = {
            'name': 'Nome da Categoria',
            'description': DESCRICAO_LABEL
        }


class UnitForm(forms.ModelForm):
    """Formulário para unidades de medida."""
    
    class Meta:
        model = Unit
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: UN, KG, L, M, CX',
                'maxlength': '20'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Unidade, Quilograma, Litro, Metro',
                'maxlength': '100'
            })
        }
        labels = {
            'name': 'Sigla/Código',
            'description': DESCRICAO_LABEL
        }


class ProductForm(forms.ModelForm):
    """Formulário para produtos."""
    
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'description', 'category', 'unit',
            'current_stock', 'min_stock', 'unit_price', 'expiry_date',
            'ncm', 'is_active'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Código único do produto',
                'pattern': '^[A-Z0-9-]+$',
                'title': 'Use apenas letras maiúsculas, números e hífen'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição detalhada do produto (opcional)',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'current_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'min_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'ncm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 12345678',
                'pattern': '[0-9]{8}',
                'title': 'NCM deve ter exatamente 8 dígitos'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'sku': 'Código (SKU)',
            'name': 'Nome',
            'description': DESCRICAO_LABEL,
            'category': 'Categoria',
            'unit': 'Unidade',
            'current_stock': 'Estoque Atual',
            'min_stock': 'Estoque Mínimo',
            'unit_price': 'Preço Unitário (R$)',
            'expiry_date': 'Data de Validade',
            'ncm': 'NCM (Código Fiscal)',
            'is_active': 'Produto Ativo'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar opção vazia para selects obrigatórios
        self.fields['category'].empty_label = "Selecione uma categoria"
        self.fields['unit'].empty_label = "Selecione uma unidade"
        
        # Marcar campos obrigatórios com asterisco
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = True
                if 'placeholder' in field.widget.attrs:
                    field.widget.attrs['placeholder'] += ' *'
    
    def clean_sku(self):
        """Validação personalizada para SKU."""
        sku = self.cleaned_data.get('sku', '').upper().strip()
        
        if not sku:
            raise ValidationError('SKU é obrigatório.')
        
        # Verificar formato
        if not re.match(r'^[A-Z0-9-]+$', sku):
            raise ValidationError('SKU deve conter apenas letras maiúsculas, números e hífen.')
        
        # Verificar unicidade (excluindo o próprio objeto na edição)
        queryset = Product.objects.filter(sku=sku)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('Já existe um produto com este SKU.')
        
        return sku
    
    def clean_current_stock(self):
        """Validação para estoque atual."""
        stock = self.cleaned_data.get('current_stock')
        if stock is not None and stock < 0:
            raise ValidationError('Estoque atual não pode ser negativo.')
        return stock
    
    def clean_min_stock(self):
        """Validação para estoque mínimo."""
        min_stock = self.cleaned_data.get('min_stock')
        if min_stock is not None and min_stock < 0:
            raise ValidationError('Estoque mínimo não pode ser negativo.')
        return min_stock
    
    def clean_unit_price(self):
        """Validação para preço unitário."""
        price = self.cleaned_data.get('unit_price')
        if price is not None and price < 0:
            raise ValidationError('Preço unitário não pode ser negativo.')
        return price
    
    def clean_expiry_date(self):
        """Validação para data de validade."""
        expiry_date = self.cleaned_data.get('expiry_date')
        if expiry_date and expiry_date <= timezone.now().date():
            raise ValidationError('Data de validade deve ser futura.')
        return expiry_date
    
    def clean_ncm(self):
        """Validação para NCM."""
        ncm = self.cleaned_data.get('ncm', '').strip()
        if ncm and not re.match(r'^\d{8}$', ncm):
            raise ValidationError('NCM deve ter exatamente 8 dígitos numéricos.')
        return ncm
    
    def clean(self):
        """Validação geral do formulário."""
        cleaned_data = super().clean()
        current_stock = cleaned_data.get('current_stock')
        min_stock = cleaned_data.get('min_stock')
        
        # Verificar se estoque atual é menor que mínimo (warning, não erro)
        if (current_stock is not None and min_stock is not None and 
            current_stock > 0 and min_stock > 0 and current_stock < min_stock):
            # Apenas adicionar uma mensagem informativa, não bloquear
            self.add_error('current_stock', 
                'Atenção: Estoque atual está abaixo do estoque mínimo.')
        
        return cleaned_data


class ProductSearchForm(forms.Form):
    """Formulário para busca e filtros de produtos."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por código, nome ou descrição...',
            'autocomplete': 'off'
        }),
        label='Buscar'
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='Todas as categorias',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Categoria'
    )
    
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        required=False,
        empty_label='Todas as unidades',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Unidade'
    )
    
    STOCK_STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('CRITICO', 'Crítico (sem estoque)'),
        ('BAIXO', 'Baixo (abaixo do mínimo)'),
        ('OK', 'OK (estoque normal)'),
    ]
    
    stock_status = forms.ChoiceField(
        choices=STOCK_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Status do Estoque'
    )
    
    ACTIVE_CHOICES = [
        ('', 'Todos'),
        ('1', 'Apenas ativos'),
        ('0', 'Apenas inativos'),
    ]
    
    active = forms.ChoiceField(
        choices=ACTIVE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Status'
    )


class ProductBulkActionForm(forms.Form):
    """Formulário para ações em lote nos produtos."""
    
    ACTION_CHOICES = [
        ('', 'Selecione uma ação'),
        ('activate', 'Ativar produtos'),
        ('deactivate', 'Desativar produtos'),
        ('update_min_stock', 'Atualizar estoque mínimo'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Ação'
    )
    
    new_min_stock = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Novo valor para estoque mínimo',
            'step': '0.01'
        }),
        label='Novo Estoque Mínimo'
    )
    
    selected_products = forms.CharField(
        widget=forms.HiddenInput(),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_min_stock = cleaned_data.get('new_min_stock')
        
        if action == 'update_min_stock' and new_min_stock is None:
            raise ValidationError('Novo estoque mínimo é obrigatório para esta ação.')
        
        return cleaned_data