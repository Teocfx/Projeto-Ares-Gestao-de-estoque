"""
Models para sistema de relatórios.
Geração e histórico de relatórios com filtros avançados.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
import json

from core.models import TimeStampedModel

# Constantes para verbose_name repetidos
TIPO_RELATORIO_VERBOSE = "Tipo de Relatório"
USUARIO_VERBOSE = "Usuário"


class ReportType(models.Model):
    """
    Tipos de relatórios disponíveis no sistema.
    """
    ESTOQUE = 'estoque'
    MOVIMENTACOES = 'movimentacoes'
    VENCIMENTOS = 'vencimentos'
    BAIXO_ESTOQUE = 'baixo_estoque'
    AUDITORIA = 'auditoria'
    
    TYPE_CHOICES = [
        (ESTOQUE, 'Relatório de Estoque'),
        (MOVIMENTACOES, 'Relatório de Movimentações'),
        (VENCIMENTOS, 'Relatório de Vencimentos'),
        (BAIXO_ESTOQUE, 'Relatório de Baixo Estoque'),
        (AUDITORIA, 'Relatório de Auditoria'),
    ]
    
    code = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        unique=True,
        verbose_name="Código"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = TIPO_RELATORIO_VERBOSE
        verbose_name_plural = "Tipos de Relatórios"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportGeneration(TimeStampedModel):
    """
    Histórico de relatórios gerados.
    Mantém registro de todos os relatórios criados.
    """
    
    STATUS_PENDING = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_ERROR = 'error'
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendente'),
        (STATUS_PROCESSING, 'Processando'),
        (STATUS_COMPLETED, 'Concluído'),
        (STATUS_ERROR, 'Erro'),
    ]
    
    FORMAT_PDF = 'pdf'
    FORMAT_EXCEL = 'excel'
    FORMAT_CSV = 'csv'
    
    FORMAT_CHOICES = [
        (FORMAT_PDF, 'PDF'),
        (FORMAT_EXCEL, 'Excel'),
        (FORMAT_CSV, 'CSV'),
    ]
    
    # Identificação do relatório
    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.PROTECT,
        verbose_name=TIPO_RELATORIO_VERBOSE
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Título"
    )
    
    # Usuário que solicitou
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reports',
        verbose_name=USUARIO_VERBOSE
    )
    
    # Parâmetros e filtros (JSON)
    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtros Aplicados",
        help_text="Filtros em formato JSON"
    )
    
    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Status"
    )
    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default=FORMAT_PDF,
        verbose_name="Formato"
    )
    
    # Resultados
    file_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Caminho do Arquivo"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Tamanho do Arquivo (bytes)"
    )
    
    # Dados do processamento
    processing_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Tempo de Processamento"
    )
    error_message = models.TextField(
        blank=True,
        verbose_name="Mensagem de Erro"
    )
    
    # Estatísticas do relatório
    total_records = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Total de Registros"
    )
    
    class Meta:
        verbose_name = "Geração de Relatório"
        verbose_name_plural = "Gerações de Relatórios"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['report_type', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    @property
    def is_ready(self):
        """Verifica se o relatório está pronto para download."""
        return self.status == self.STATUS_COMPLETED and self.file_path
    
    @property
    def file_size_formatted(self):
        """Retorna o tamanho do arquivo formatado."""
        if not self.file_size:
            return "-"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def get_download_url(self):
        """Retorna URL para download do relatório."""
        if self.is_ready:
            return reverse('relatorios:download', kwargs={'pk': self.pk})
        return None


class ReportTemplate(TimeStampedModel):
    """
    Templates personalizados para relatórios.
    Permite salvar configurações de filtros.
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do Template"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição"
    )
    
    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.CASCADE,
        verbose_name=TIPO_RELATORIO_VERBOSE
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_templates',
        verbose_name=USUARIO_VERBOSE
    )
    
    # Configurações salvas
    filters = models.JSONField(
        default=dict,
        verbose_name="Filtros Salvos"
    )
    format = models.CharField(
        max_length=10,
        choices=ReportGeneration.FORMAT_CHOICES,
        default=ReportGeneration.FORMAT_PDF,
        verbose_name="Formato Padrão"
    )
    
    is_public = models.BooleanField(
        default=False,
        verbose_name="Público",
        help_text="Disponível para outros usuários"
    )
    
    class Meta:
        verbose_name = "Template de Relatório"
        verbose_name_plural = "Templates de Relatórios"
        ordering = ['name']
        unique_together = ['user', 'name', 'report_type']
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"


class ReportSchedule(TimeStampedModel):
    """
    Agendamento de relatórios automáticos.
    Para futuras implementações de relatórios recorrentes.
    """
    
    FREQUENCY_DAILY = 'daily'
    FREQUENCY_WEEKLY = 'weekly'
    FREQUENCY_MONTHLY = 'monthly'
    
    FREQUENCY_CHOICES = [
        (FREQUENCY_DAILY, 'Diário'),
        (FREQUENCY_WEEKLY, 'Semanal'),
        (FREQUENCY_MONTHLY, 'Mensal'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name="Nome do Agendamento"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='report_schedules',
        verbose_name=USUARIO_VERBOSE
    )
    
    report_type = models.ForeignKey(
        ReportType,
        on_delete=models.CASCADE,
        verbose_name=TIPO_RELATORIO_VERBOSE
    )
    
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        verbose_name="Frequência"
    )
    
    filters = models.JSONField(
        default=dict,
        verbose_name="Filtros"
    )
    
    format = models.CharField(
        max_length=10,
        choices=ReportGeneration.FORMAT_CHOICES,
        default=ReportGeneration.FORMAT_PDF,
        verbose_name="Formato"
    )
    
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Próxima Execução"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    class Meta:
        verbose_name = "Agendamento de Relatório"
        verbose_name_plural = "Agendamentos de Relatórios"
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
