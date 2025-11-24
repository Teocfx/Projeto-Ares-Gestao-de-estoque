"""
Forms para sistema de relatórios.
Formulários para geração e filtros de relatórios.
"""

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date

from .models import ReportGeneration, ReportType, ReportTemplate
from produtos.models import Product, Category
from movimentacoes.models import InventoryMovement


class ReportGenerationForm(forms.ModelForm):
    """
    Formulário para gerar novos relatórios.
    """
    
    class Meta:
        model = ReportGeneration
        fields = ['report_type', 'title', 'format', 'filters']
        widgets = {
            'report_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Relatório de Estoque - Janeiro 2024',
                'required': True,
            }),
            'format': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'filters': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customizar queryset de tipos ativos
        self.fields['report_type'].queryset = ReportType.objects.filter(is_active=True)
        self.fields['report_type'].empty_label = "Selecione o tipo de relatório..."
        
        # Labels
        self.fields['report_type'].label = "Tipo de Relatório"
        self.fields['title'].label = "Título do Relatório"
        self.fields['format'].label = "Formato de Saída"
        
        # Help texts
        self.fields['title'].help_text = "Nome para identificar este relatório"
        self.fields['format'].help_text = "Formato do arquivo a ser gerado"


class ReportFilterForm(forms.Form):
    """
    Formulário genérico para filtros de relatórios.
    """
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label="Data Inicial"
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        }),
        label="Data Final"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_from > date_to:
                raise ValidationError("Data inicial deve ser anterior à data final.")
            
            # Limitar período máximo (ex: 2 anos)
            max_period = timedelta(days=730)
            if (date_to - date_from) > max_period:
                raise ValidationError("Período máximo permitido: 2 anos.")
        
        return cleaned_data


class StockReportForm(ReportFilterForm):
    """
    Formulário específico para relatórios de estoque.
    """
    
    STOCK_STATUS_CHOICES = [
        ('', 'Todos os status'),
        ('ok', 'Estoque OK'),
        ('baixo', 'Estoque Baixo'),
        ('critico', 'Estoque Crítico'),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou SKU do produto...',
        }),
        label="Buscar Produto"
    )
    
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.filter(is_active=True),
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Categoria"
    )
    
    stock_status = forms.ChoiceField(
        required=False,
        choices=STOCK_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Status do Estoque"
    )
    
    include_inactive = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Incluir produtos inativos"
    )


class MovementReportForm(ReportFilterForm):
    """
    Formulário específico para relatórios de movimentações.
    """
    
    movement_type = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + InventoryMovement.TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Tipo de Movimentação"
    )
    
    product = forms.ModelChoiceField(
        required=False,
        queryset=Product.objects.filter(is_active=True),
        empty_label="Todos os produtos",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Produto Específico"
    )
    
    user = forms.ModelChoiceField(
        required=False,
        queryset=None,  # Será preenchido no __init__
        empty_label="Todos os usuários",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Usuário"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Preencher usuários que fizeram movimentações
        from django.contrib.auth import get_user_model
        user_model = get_user_model()
        
        self.fields['user'].queryset = user_model.objects.filter(
            inventory_movements__isnull=False
        ).distinct().order_by('first_name', 'username')


class ExpiryReportForm(forms.Form):
    """
    Formulário específico para relatórios de vencimentos.
    """
    
    days_ahead = forms.IntegerField(
        initial=30,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'max': '365',
        }),
        label="Dias à frente",
        help_text="Produtos que vencem nos próximos X dias"
    )
    
    include_expired = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Incluir produtos já vencidos"
    )
    
    category = forms.ModelChoiceField(
        required=False,
        queryset=Category.objects.filter(is_active=True),
        empty_label="Todas as categorias",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Categoria"
    )
    
    min_stock_value = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
        }),
        label="Estoque mínimo",
        help_text="Mostrar apenas produtos com estoque maior que este valor"
    )


class ReportTemplateForm(forms.ModelForm):
    """
    Formulário para salvar templates de relatórios.
    """
    
    class Meta:
        model = ReportTemplate
        fields = ['name', 'description', 'report_type', 'format', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'placeholder': 'Ex: Estoque Mensal Categoria A',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do template...',
            }),
            'report_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'format': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apenas tipos ativos
        self.fields['report_type'].queryset = ReportType.objects.filter(is_active=True)
        
        # Labels
        self.fields['name'].label = "Nome do Template"
        self.fields['description'].label = "Descrição"
        self.fields['report_type'].label = "Tipo de Relatório"
        self.fields['format'].label = "Formato Padrão"
        self.fields['is_public'].label = "Compartilhar com outros usuários"
        
        # Help texts
        self.fields['name'].help_text = "Nome único para identificar este template"
        self.fields['is_public'].help_text = "Permite que outros usuários usem este template"


class QuickReportForm(forms.Form):
    """
    Formulário simplificado para relatórios rápidos.
    """
    
    QUICK_REPORTS = [
        ('stock_summary', 'Resumo de Estoque'),
        ('low_stock', 'Produtos com Estoque Baixo'),
        ('recent_movements', 'Movimentações Recentes (7 dias)'),
        ('expiring_soon', 'Produtos Vencendo (30 dias)'),
        ('stock_by_category', 'Estoque por Categoria'),
    ]
    
    report_type = forms.ChoiceField(
        choices=QUICK_REPORTS,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True,
        }),
        label="Relatório Rápido"
    )
    
    format = forms.ChoiceField(
        choices=ReportGeneration.FORMAT_CHOICES,
        initial=ReportGeneration.FORMAT_PDF,
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Formato"
    )
    
    send_email = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
        label="Enviar por email",
        help_text="Enviar relatório para seu email após a geração"
    )