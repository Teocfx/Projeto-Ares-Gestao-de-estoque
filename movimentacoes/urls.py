"""
URLs do app Movimentações.
Rotas completas para CRUD de movimentações e APIs.
"""
from django.urls import path
from . import views

app_name = 'movimentacoes'

urlpatterns = [
    # URLs principais
    path('', views.MovementListView.as_view(), name='list'),
    path('registrar/', views.MovementCreateView.as_view(), name='create'),
    path('<int:pk>/', views.MovementDetailView.as_view(), name='detail'),
    
    # URLs funcionais para compatibilidade
    path('list/', views.list_movimentacoes, name='list_func'),
    path('create/', views.create_movimentacao, name='create_func'),
    path('detail/<int:pk>/', views.detail_movimentacao, name='detail_func'),
    
    # APIs/AJAX
    path('api/product-stock/<int:product_id>/', views.get_product_stock, name='product_stock'),
    path('api/statistics/', views.movement_statistics, name='statistics'),
]
