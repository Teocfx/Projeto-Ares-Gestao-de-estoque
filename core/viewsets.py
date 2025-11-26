"""
ViewSets para API REST do core (auditoria, perfis, usuários).
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter, NumberFilter, DateTimeFilter
from django.contrib.auth import get_user_model
from django.db.models import Count

from .models import AuditLog, PerfilUsuario
from .serializers import (
    UserSerializer,
    PerfilUsuarioSerializer,
    AuditLogSerializer,
    AuditLogStatsSerializer,
)
from .permissions import IsAdminUser as IsAdminUserPermission

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualização de usuários.
    
    list: Listar todos os usuários (apenas admin)
    retrieve: Obter detalhes de um usuário
    me: Obter dados do usuário autenticado
    """
    queryset = User.objects.filter(is_active=True).select_related('profile')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined', 'last_login']
    ordering = ['username']
    
    def get_queryset(self):
        """Admins veem todos, outros veem apenas a si mesmos."""
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Retorna dados do usuário autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class PerfilUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualização de perfis de usuários.
    
    list: Listar todos os perfis (apenas admin)
    retrieve: Obter detalhes de um perfil
    stats: Estatísticas de perfis por tipo
    """
    queryset = PerfilUsuario.objects.all().select_related('user', 'autorizado_por')
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated, IsAdminUserPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['perfil', 'ativo']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'perfil']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas de perfis por tipo."""
        from .models import PerfilAcesso
        queryset = self.get_queryset()
        
        stats = {
            'total_profiles': queryset.count(),
            'by_perfil': list(
                queryset.values('perfil')
                .annotate(count=Count('id'))
                .order_by('perfil')
            ),
            'representante_legal_count': queryset.filter(perfil=PerfilAcesso.REPRESENTANTE_LEGAL).count(),
            'representante_delegado_count': queryset.filter(perfil=PerfilAcesso.REPRESENTANTE_DELEGADO).count(),
            'operador_count': queryset.filter(perfil=PerfilAcesso.OPERADOR).count(),
            'ativos_count': queryset.filter(ativo=True).count(),
            'inativos_count': queryset.filter(ativo=False).count(),
        }
        
        return Response(stats)


class AuditLogFilter(FilterSet):
    """Filtros para AuditLog."""
    user = NumberFilter(field_name='user__id')
    action = CharFilter(field_name='action')
    content_type = NumberFilter(field_name='content_type__id')
    model = CharFilter(field_name='content_type__model', lookup_expr='icontains')
    object_id = CharFilter(field_name='object_id')
    date_from = DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    date_to = DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    
    class Meta:
        model = AuditLog
        fields = ['user', 'action', 'content_type']


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para visualização de logs de auditoria (somente leitura).
    
    list: Listar todos os logs de auditoria
    retrieve: Obter detalhes de um log
    stats: Estatísticas de auditoria
    by_user: Logs de um usuário específico
    by_model: Logs de um model específico
    """
    queryset = AuditLog.objects.all().select_related('user', 'content_type')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminUserPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ['object_repr', 'changes', 'user__username']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas de logs de auditoria."""
        queryset = self.get_queryset()
        
        # Filtrar por período se fornecido
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        total_logs = queryset.count()
        total_creates = queryset.filter(action=AuditLog.CREATE).count()
        total_updates = queryset.filter(action=AuditLog.UPDATE).count()
        total_deletes = queryset.filter(action=AuditLog.DELETE).count()
        
        most_active_users = list(
            queryset.values('user__username', 'user__first_name', 'user__last_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        most_modified_models = list(
            queryset.values('content_type__model', 'content_type__app_label')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        recent_logs = queryset[:20]
        
        stats = {
            'total_logs': total_logs,
            'total_creates': total_creates,
            'total_updates': total_updates,
            'total_deletes': total_deletes,
            'most_active_users': most_active_users,
            'most_modified_models': most_modified_models,
            'recent_logs': recent_logs,
        }
        
        serializer = AuditLogStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Lista logs de um usuário específico."""
        user_id = request.query_params.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(user_id=user_id)
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Lista logs de um model específico."""
        model_name = request.query_params.get('model')
        
        if not model_name:
            return Response(
                {'error': 'model é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logs = self.get_queryset().filter(content_type__model=model_name.lower())
        
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
