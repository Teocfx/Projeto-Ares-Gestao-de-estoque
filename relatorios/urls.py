"""
URLs do app Relatórios.
Sistema completo de geração e visualização de relatórios.
"""
from django.urls import path
from . import views

app_name = 'relatorios'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    
    # Geração de relatórios
    path('gerar/', views.generate_report, name='generate'),
    path('gerar/personalizado/', views.generate_custom_report, name='generate_custom'),
    path('detalhes/<int:pk>/', views.report_detail, name='detail'),
    path('download/<int:pk>/', views.download_report, name='download'),
    
    # Relatórios específicos por tipo
    path('estoque/', views.relatorio_estoque, name='estoque'),
    path('movimentacoes/', views.relatorio_movimentacoes, name='movimentacoes'),
    path('vencimentos/', views.relatorio_vencimentos, name='vencimentos'),
    path('financeiro/', views.relatorio_financeiro, name='financeiro'),
    
    # Downloads PDF
    path('download/estoque/', views.download_estoque_pdf, name='download_estoque_pdf'),
    path('download/movimentacoes/', views.download_movimentacoes_pdf, name='download_movimentacoes_pdf'),
    path('download/vencimentos/', views.download_vencimentos_pdf, name='download_vencimentos_pdf'),
    path('download/financeiro/', views.download_financeiro_pdf, name='download_financeiro_pdf'),
    
    # URLs legadas para compatibilidade
    path('stock/', views.relatorio_estoque, name='stock'),
    path('movements/', views.relatorio_movimentacoes, name='movements'),
    path('expiry/', views.relatorio_vencimentos, name='expiry'),
]
