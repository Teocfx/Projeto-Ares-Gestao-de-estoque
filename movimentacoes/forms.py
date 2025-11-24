"""
Forms para movimentações de estoque.
Validações de negócio e interface responsiva.
"""

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import InventoryMovement
from produtos.models import Product


class InventoryMovementForm(forms.ModelForm):
    """
    Form para criar/editar movimentações de estoque.
    Inclui validações de negócio e widgets responsivos.
    """

    class Meta:
        model = InventoryMovement
        fields = ['product', 'type', 'quantity', 'document', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'onchange': 'updateProductInfo(this.value)'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'onchange': 'updateFormBehavior(this.value)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'required': True,
                'placeholder': 'Ex: 10.50'
            }),
            'document': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: NF-123456, CF-e 789',
                'maxlength': 100
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais sobre a movimentação...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizar queryset de produtos (apenas ativos)
        self.fields['product'].queryset = Product.objects.filter(
            is_active=True
        ).select_related('category', 'unit').order_by('name')
        
        # Adicionar empty_label
        self.fields['product'].empty_label = "Selecione um produto..."
        
        # Labels personalizadas
        self.fields['product'].label = "Produto"
        self.fields['type'].label = "Tipo de Movimentação"
        self.fields['quantity'].label = "Quantidade"
        self.fields['document'].label = "Documento (opcional)"
        self.fields['notes'].label = "Observações (opcional)"
        
        # Help texts
        self.fields['quantity'].help_text = "Quantidade a ser movimentada"
        self.fields['document'].help_text = "Número da NF, CF-e ou outro documento de referência"
        self.fields['notes'].help_text = "Informações adicionais sobre esta movimentação"

    def clean_quantity(self):
        """Validar quantidade baseada no tipo de movimentação."""
        quantity = self.cleaned_data.get('quantity')
        movement_type = self.cleaned_data.get('type')
        product = self.cleaned_data.get('product')
        
        if not quantity or quantity <= 0:
            raise ValidationError("A quantidade deve ser maior que zero.")
        
        if movement_type == InventoryMovement.SAIDA and product:
            # Verificar se há estoque suficiente para saída
            if quantity > product.current_stock:
                raise ValidationError(
                    f"Estoque insuficiente. Disponível: {product.current_stock} {product.unit.name}"
                )
        
        return quantity

    def clean(self):
        """Validações cruzadas entre campos."""
        cleaned_data = super().clean()
        movement_type = cleaned_data.get('type')
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if not all([movement_type, product, quantity]):
            return cleaned_data
        
        # Validações específicas por tipo
        if movement_type == InventoryMovement.AJUSTE:
            # Para ajustes, a quantidade não pode ser negativa
            if quantity < 0:
                raise ValidationError({
                    'quantity': "Para ajustes, informe o valor final desejado (não pode ser negativo)."
                })
        
        elif movement_type == InventoryMovement.ENTRADA:
            # Para entradas, verificar se não é uma quantidade muito grande
            max_reasonable = Decimal('999999.99')
            if quantity > max_reasonable:
                raise ValidationError({
                    'quantity': f"Quantidade muito alta. Máximo permitido: {max_reasonable}"
                })
        
        return cleaned_data  # noqa: R504 - Retorno padrão Django forms


class MovementFilterForm(forms.Form):
    """
    Form para filtros na listagem de movimentações.
    """
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por produto, documento ou observações...',
        }),
        label="Buscar"
    )
    
    type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + InventoryMovement.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Tipo"
    )
    
    product = forms.ModelChoiceField(
        required=False,
        queryset=Product.objects.filter(is_active=True).order_by('name'),
        empty_label="Todos os produtos",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Produto"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label="Data inicial"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label="Data final"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes Bootstrap para layout responsivo
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'data-filter-field': field_name
            })


class BulkMovementForm(forms.Form):
    """
    Form para movimentações em lote (funcionalidade futura).
    """
    
    type = forms.ChoiceField(
        choices=InventoryMovement.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        }),
        label="Tipo de Movimentação"
    )
    
    document = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Documento de referência para todas as movimentações'
        }),
        label="Documento"
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observações gerais...'
        }),
        label="Observações"
    )
    
    # Campo para upload de CSV (funcionalidade futura)
    csv_file = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv',
        }),
        label="Arquivo CSV",
        help_text="Upload de arquivo CSV com: produto_id, quantidade"
    )