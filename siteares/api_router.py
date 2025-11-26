"""
Routers da API REST (v1).

Registra todos os viewsets e define as rotas da API.
"""
from rest_framework.routers import DefaultRouter

from produtos.viewsets import CategoryViewSet, UnitViewSet, ProductViewSet
from movimentacoes.viewsets import InventoryMovementViewSet
from core.viewsets import UserViewSet, PerfilUsuarioViewSet, AuditLogViewSet

# Router principal
router = DefaultRouter()

# Produtos
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'products', ProductViewSet, basename='product')

# Movimentações
router.register(r'movements', InventoryMovementViewSet, basename='movement')

# Core (usuários, perfis, auditoria)
router.register(r'users', UserViewSet, basename='user')
router.register(r'perfis', PerfilUsuarioViewSet, basename='perfil')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = router.urls
