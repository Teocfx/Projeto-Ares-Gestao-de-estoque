"""
URLs para o app produtos.
Rotas completas para CRUD de produtos, categorias e unidades.
"""

from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    # URLs de Produtos
    path('', views.ProductListView.as_view(), name='list'),
    path('novo/', views.ProductCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/editar/', views.ProductUpdateView.as_view(), name='update'),
    path('<int:pk>/deletar/', views.ProductDeleteView.as_view(), name='delete'),
    
    # URLs de Categorias
    path('categorias/', views.CategoryListView.as_view(), name='category_list'),
    path('categorias/nova/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categorias/<int:pk>/editar/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categorias/<int:pk>/deletar/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # URLs de Unidades
    path('unidades/', views.UnitListView.as_view(), name='unit_list'),
    path('unidades/nova/', views.UnitCreateView.as_view(), name='unit_create'),
    path('unidades/<int:pk>/editar/', views.UnitUpdateView.as_view(), name='unit_update'),
    path('unidades/<int:pk>/deletar/', views.UnitDeleteView.as_view(), name='unit_delete'),
    
    # APIs/AJAX
    path('api/bulk-action/', views.ProductBulkActionView.as_view(), name='bulk_action'),
    path('api/autocomplete/', views.product_autocomplete, name='autocomplete'),
    path('api/dashboard/', views.dashboard_products, name='dashboard_api'),
]
