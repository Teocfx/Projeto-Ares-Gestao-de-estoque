"""
Serializers para API REST do core (auditoria, perfis, configurações).
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import AuditLog, PerfilUsuario

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para User (django.contrib.auth)."""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    perfil_tipo = serializers.SerializerMethodField()
    perfil_display = serializers.SerializerMethodField()
    perfil_ativo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'is_active',
            'is_staff',
            'perfil_tipo',
            'perfil_display',
            'perfil_ativo',
            'date_joined',
            'last_login',
        ]
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
            'is_staff',
        ]
    
    def get_perfil_tipo(self, obj):
        """Retorna tipo do perfil do usuário."""
        if hasattr(obj, 'perfil'):
            return obj.perfil.perfil
        return None
    
    def get_perfil_display(self, obj):
        """Retorna display name do perfil."""
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_perfil_display()
        return None
    
    def get_perfil_ativo(self, obj):
        """Retorna se o perfil está ativo."""
        if hasattr(obj, 'perfil'):
            return obj.perfil.ativo
        return False


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para PerfilUsuario."""
    
    user = UserSerializer(read_only=True)
    perfil_display = serializers.CharField(source='get_perfil_display', read_only=True)
    autorizado_por_nome = serializers.CharField(
        source='autorizado_por.get_full_name', 
        read_only=True
    )
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'id',
            'user',
            'perfil',
            'perfil_display',
            'autorizado_por_nome',
            'permissions',
            'ativo',
            'data_expiracao',
            'observacoes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_permissions(self, obj):
        """Retorna lista de permissões do perfil."""
        return {
            'pode_gerenciar_usuarios': obj.pode_gerenciar_usuarios(),
            'pode_aprovar_movimentacoes': obj.pode_aprovar_movimentacoes(),
            'pode_editar_produtos': obj.pode_editar_produtos(),
            'pode_visualizar_relatorios': obj.pode_visualizar_relatorios(),
            'is_representante_legal': obj.is_representante_legal(),
            'is_representante_delegado': obj.is_representante_delegado(),
            'is_operador': obj.is_operador(),
        }


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer para AuditLog."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user_name',
            'user_username',
            'action',
            'action_display',
            'content_type_name',
            'object_id',
            'object_repr',
            'changes',
            'ip_address',
            'user_agent',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_content_type_name(self, obj):
        """Retorna nome legível do content_type."""
        if obj.content_type:
            return obj.content_type.model
        return None


class AuditLogStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de auditoria."""
    
    total_logs = serializers.IntegerField()
    total_creates = serializers.IntegerField()
    total_updates = serializers.IntegerField()
    total_deletes = serializers.IntegerField()
    most_active_users = serializers.ListField()
    most_modified_models = serializers.ListField()
    recent_logs = AuditLogSerializer(many=True)


class ContentTypeSerializer(serializers.ModelSerializer):
    """Serializer para ContentType."""
    
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']
        read_only_fields = ['id', 'app_label', 'model']
