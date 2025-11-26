"""
URLs da API REST v1.

Inclui:
- JWT Authentication endpoints
- Swagger/OpenAPI documentation
- API endpoints (produtos, movimentações, auditoria)
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="ARES - Sistema de Gestão de Estoque API",
        default_version='v1',
        description="""
        API REST completa do Sistema ARES de Gestão de Estoque.
        
        ## Autenticação
        Esta API utiliza JWT (JSON Web Tokens) para autenticação.
        
        ### Como obter token:
        1. POST /api/v1/auth/token/ com {username, password}
        2. Receba {access, refresh} tokens
        3. Use o access token no header: `Authorization: Bearer <token>`
        
        ### Endpoints de Auth:
        - `/api/v1/auth/token/` - Obter access e refresh tokens
        - `/api/v1/auth/token/refresh/` - Renovar access token
        - `/api/v1/auth/token/verify/` - Verificar validade de token
        
        ## Recursos Principais
        
        ### Produtos
        - Categorias, Unidades, Produtos
        - Filtros avançados, busca, paginação
        - Actions: low_stock, expired, stats
        
        ### Movimentações
        - Entrada, Saída, Ajuste de estoque
        - Atualização automática de estoque
        - Bulk create (lote)
        - Stats por período
        
        ### Core
        - Usuários e perfis
        - Logs de auditoria
        - Estatísticas gerais
        
        ## Permissões
        - Representante Legal: Acesso total
        - Representante Delegado: Acesso administrativo
        - Operador: Acesso operacional básico
        
        ## Rate Limiting
        - Anônimo: 100 requisições/hora
        - Autenticado: 1000 requisições/hora
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contato@ares.pb.gov.br"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

app_name = 'api-v1'

urlpatterns = [
    # JWT Authentication
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Swagger/OpenAPI Documentation
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # API Endpoints
    path('', include('siteares.api_router')),
]
