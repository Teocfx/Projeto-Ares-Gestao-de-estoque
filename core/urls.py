from django.urls import path
from .views import DocumentServeView, document_serve_inline, TesteComponentesView

app_name = 'core'

urlpatterns = [
    # View customizada para servir documentos inline (classe) - Reutilizável por qualquer app
    path('documents/view/<int:document_id>/<str:document_filename>', DocumentServeView.as_view(), name='document_serve_inline'),
    
    # View alternativa (função) - Versão simplificada
    # path('documents/view/<int:document_id>/<str:document_filename>', document_serve_inline, name='document_serve_inline'),
    
    # Teste de componentes (apenas desenvolvimento)
    path('teste-componentes/', TesteComponentesView.as_view(), name='teste_componentes'),
]