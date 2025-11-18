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
    path('detalhes/<int:pk>/', views.report_detail, name='detail'),
    path('download/<int:pk>/', views.download_report, name='download'),
    
    # Relatórios específicos por tipo
    path('estoque/', views.relatorio_estoque, name='estoque'),
    path('movimentacoes/', views.relatorio_movimentacoes, name='movimentacoes'),
    path('vencimentos/', views.relatorio_vencimentos, name='vencimentos'),
    
    # URLs legadas para compatibilidade
    path('stock/', views.relatorio_estoque, name='stock'),
    path('movements/', views.relatorio_movimentacoes, name='movements'),
    path('expiry/', views.relatorio_vencimentos, name='expiry'),
]
