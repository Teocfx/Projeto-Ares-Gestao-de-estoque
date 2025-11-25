from django.urls import path
from .views import (
    DocumentServeView, 
    document_serve_inline, 
    TesteComponentesView,
    AuditLogListView,
    AuditLogDetailView
)
from .upload_views import (
    FileUploadView,
    ImageUploadView,
    DocumentUploadView,
    ProductImageUploadView,
    AvatarUploadView
)

app_name = 'core'

urlpatterns = [
    # View customizada para servir documentos inline (classe) - Reutilizável por qualquer app
    path('documents/view/<int:document_id>/<str:document_filename>', DocumentServeView.as_view(), name='document_serve_inline'),
    
    # View alternativa (função) - Versão simplificada
    # path('documents/view/<int:document_id>/<str:document_filename>', document_serve_inline, name='document_serve_inline'),
    
    # Teste de componentes (apenas desenvolvimento)
    path('teste-componentes/', TesteComponentesView.as_view(), name='teste_componentes'),
    
    # Logs de Auditoria
    path('logs/', AuditLogListView.as_view(), name='audit_log_list'),
    path('logs/<int:pk>/', AuditLogDetailView.as_view(), name='audit_log_detail'),
    
    # Upload de Arquivos
    path('upload/file/', FileUploadView.as_view(), name='upload_file'),
    path('upload/image/', ImageUploadView.as_view(), name='upload_image'),
    path('upload/document/', DocumentUploadView.as_view(), name='upload_document'),
    path('upload/product-image/', ProductImageUploadView.as_view(), name='upload_product_image'),
    path('upload/avatar/', AvatarUploadView.as_view(), name='upload_avatar'),
    
    # Exemplo de Upload (desenvolvimento)
    path('upload-exemplo/', lambda request: __import__('django.shortcuts').shortcuts.render(request, 'core/upload_exemplo.html'), name='upload_exemplo'),
]