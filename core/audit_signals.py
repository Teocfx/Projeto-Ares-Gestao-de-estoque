"""
Signals para auditoria automática de ações no sistema.

Este módulo captura automaticamente mudanças em models importantes
e registra no log de auditoria.
"""
import threading

from django.db.models.signals import post_save, post_delete, pre_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

from .models import AuditLog, TipoAcaoAuditoria, NivelSeveridade, PerfilUsuario


# Thread-local storage para o request atual
_thread_locals = threading.local()


def get_current_request():
    """Retorna o request atual do thread local."""
    return getattr(_thread_locals, 'request', None)


def set_current_request(request):
    """Define o request atual no thread local."""
    _thread_locals.request = request


class CurrentRequestMiddleware:
    """
    Middleware para armazenar o request atual no thread local.
    Adicione ao MIDDLEWARE em settings.py.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        set_current_request(None)
        return response


# Lista de models que devem ser auditados automaticamente
AUDITED_MODELS = []


def register_for_audit(model):
    """
    Decorator para registrar models para auditoria automática.
    
    Usage:
        @register_for_audit
        class MeuModel(models.Model):
            ...
    """
    AUDITED_MODELS.append(model)
    return model


def get_model_changes(instance, old_instance=None):
    """
    Compara duas instâncias e retorna as mudanças.
    
    Returns:
        dict: {field_name: {'old': old_value, 'new': new_value}}
    """
    if not old_instance:
        return {}
    
    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        
        # Ignora campos automáticos e alguns específicos
        if field_name in ['id', 'created_at', 'updated_at']:
            continue
        
        old_value = getattr(old_instance, field_name, None)
        new_value = getattr(instance, field_name, None)
        
        # Se são diferentes
        if old_value != new_value:
            changes[field_name] = {
                'old': str(old_value),
                'new': str(new_value),
            }
    
    return changes


# Signal handlers para modelos auditados

@receiver(post_save)
def audit_model_save(sender, instance, created, **kwargs):
    """Audita criação e atualização de modelos."""
    # Verifica se o modelo deve ser auditado
    if sender not in AUDITED_MODELS:
        return
    
    # Ignora o próprio AuditLog
    if sender == AuditLog:
        return
    
    request = get_current_request()
    user = getattr(request, 'user', None) if request and hasattr(request, 'user') else None
    
    # Se não tem usuário autenticado, não audita (ações de sistema)
    if not user or not user.is_authenticated:
        return
    
    action = TipoAcaoAuditoria.CREATE if created else TipoAcaoAuditoria.UPDATE
    description = f"{'Criou' if created else 'Atualizou'} {sender._meta.verbose_name}: {instance}"
    
    # Para updates, captura mudanças
    changes = {}
    if not created and hasattr(instance, '_old_instance'):
        changes = get_model_changes(instance, instance._old_instance)
    
    severity = NivelSeveridade.MEDIUM if created else NivelSeveridade.LOW
    
    AuditLog.log_action(
        user=user,
        action=action,
        description=description,
        content_object=instance,
        severity=severity,
        changes=changes,
        request=request
    )


@receiver(post_delete)
def audit_model_delete(sender, instance, **kwargs):
    """Audita exclusão de modelos."""
    if sender not in AUDITED_MODELS:
        return
    
    if sender == AuditLog:
        return
    
    request = get_current_request()
    user = getattr(request, 'user', None) if request and hasattr(request, 'user') else None
    
    if not user or not user.is_authenticated:
        return
    
    AuditLog.log_action(
        user=user,
        action=TipoAcaoAuditoria.DELETE,
        description=f"Excluiu {sender._meta.verbose_name}: {instance}",
        content_object=None,  # Objeto já foi deletado
        severity=NivelSeveridade.HIGH,
        metadata={
            'model': sender._meta.model_name,
            'object_repr': str(instance)
        },
        request=request
    )


@receiver(pre_save)
def store_old_instance(sender, instance, **kwargs):
    """Armazena instância antiga antes de salvar para comparar mudanças."""
    if sender not in AUDITED_MODELS:
        return
    
    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


# Signals de autenticação

@receiver(user_logged_in)
def audit_login(sender, request, user, **kwargs):
    """Audita login de usuário."""
    AuditLog.log_action(
        user=user,
        action=TipoAcaoAuditoria.LOGIN,
        description=f"Login realizado por {user.get_full_name() or user.username}",
        severity=NivelSeveridade.LOW,
        request=request
    )


@receiver(user_logged_out)
def audit_logout(sender, request, user, **kwargs):
    """Audita logout de usuário."""
    if user:
        AuditLog.log_action(
            user=user,
            action=TipoAcaoAuditoria.LOGOUT,
            description=f"Logout realizado por {user.get_full_name() or user.username}",
            severity=NivelSeveridade.LOW,
            request=request
        )


@receiver(user_login_failed)
def audit_login_failed(sender, credentials, request, **kwargs):
    """Audita tentativas falhas de login."""
    username = credentials.get('username', 'desconhecido')
    
    AuditLog.log_action(
        user=None,
        action=TipoAcaoAuditoria.LOGIN,
        description=f"Tentativa de login falha para usuário: {username}",
        severity=NivelSeveridade.MEDIUM,
        metadata={'username': username},
        request=request
    )


# Signal para mudanças de perfil (crítico)

@receiver(post_save, sender=PerfilUsuario)
def audit_perfil_change(sender, instance, created, **kwargs):
    """Audita mudanças em perfis de usuário (operação crítica)."""
    request = get_current_request()
    user = getattr(request, 'user', None) if request and hasattr(request, 'user') else None
    
    if not user or not user.is_authenticated:
        return
    
    if created:
        description = f"Criou perfil {instance.get_perfil_display()} para {instance.user.get_full_name()}"
    else:
        description = f"Alterou perfil de {instance.user.get_full_name()}"
    
    changes = {}
    if not created and hasattr(instance, '_old_instance'):
        old = instance._old_instance
        if old.perfil != instance.perfil:
            changes['perfil'] = {
                'old': old.get_perfil_display(),
                'new': instance.get_perfil_display()
            }
        if old.ativo != instance.ativo:
            changes['ativo'] = {
                'old': 'Ativo' if old.ativo else 'Inativo',
                'new': 'Ativo' if instance.ativo else 'Inativo'
            }
    
    AuditLog.log_action(
        user=user,
        action=TipoAcaoAuditoria.PERMISSION_CHANGE,
        description=description,
        content_object=instance,
        severity=NivelSeveridade.CRITICAL,
        changes=changes,
        request=request
    )


# Funções helper para auditoria manual

def audit_export(user, model_name, count, request=None):
    """Registra exportação de dados."""
    AuditLog.log_action(
        user=user,
        action=TipoAcaoAuditoria.EXPORT,
        description=f"Exportou {count} registros de {model_name}",
        severity=NivelSeveridade.MEDIUM,
        metadata={'model': model_name, 'count': count},
        request=request
    )


def audit_import(user, model_name, count, request=None):
    """Registra importação de dados."""
    AuditLog.log_action(
        user=user,
        action=TipoAcaoAuditoria.IMPORT,
        description=f"Importou {count} registros para {model_name}",
        severity=NivelSeveridade.HIGH,
        metadata={'model': model_name, 'count': count},
        request=request
    )


def audit_approval(user, object_repr, approved, request=None):
    """Registra aprovação/rejeição."""
    action = TipoAcaoAuditoria.APPROVE if approved else TipoAcaoAuditoria.REJECT
    description = f"{'Aprovou' if approved else 'Rejeitou'}: {object_repr}"
    
    AuditLog.log_action(
        user=user,
        action=action,
        description=description,
        severity=NivelSeveridade.MEDIUM,
        request=request
    )
