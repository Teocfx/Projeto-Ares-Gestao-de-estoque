"""
Sistema de controle de acesso baseado em perfis.

Decorators e mixins para proteger views com base nos perfis de acesso.
"""
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic.base import View

from .models import PerfilAcesso, PerfilUsuario


def require_perfil(*perfis_permitidos):
    """
    Decorator para views que requer perfis específicos.
    
    Usage:
        @require_perfil(PerfilAcesso.REPRESENTANTE_LEGAL)
        def minha_view(request):
            ...
        
        @require_perfil(PerfilAcesso.REPRESENTANTE_LEGAL, PerfilAcesso.REPRESENTANTE_DELEGADO)
        def outra_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                perfil = request.user.perfil
                
                # Verifica se o perfil está ativo
                if not perfil.ativo:
                    messages.error(request, 'Seu perfil de acesso está desativado.')
                    return redirect('dashboard:index')
                
                # Verifica se o perfil está expirado
                if perfil.data_expiracao:
                    from django.utils import timezone
                    if timezone.now().date() > perfil.data_expiracao:
                        messages.error(request, 'Seu perfil de acesso expirou.')
                        return redirect('dashboard:index')
                
                # Verifica se o perfil está na lista de permitidos
                if perfil.perfil not in perfis_permitidos:
                    messages.error(
                        request, 
                        f'Acesso negado. Esta funcionalidade requer perfil: {", ".join([p.label for p in perfis_permitidos])}'
                    )
                    raise PermissionDenied
                
                return view_func(request, *args, **kwargs)
                
            except PerfilUsuario.DoesNotExist:
                messages.error(request, 'Usuário sem perfil de acesso configurado.')
                return redirect('dashboard:index')
        
        return _wrapped_view
    return decorator


def require_permissao(permissao):
    """
    Decorator para views que requer permissão específica.
    
    Usage:
        @require_permissao('editar_produtos')
        def editar_produto(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            try:
                perfil = request.user.perfil
                
                if not perfil.tem_permissao(permissao):
                    messages.error(
                        request, 
                        f'Acesso negado. Você não tem permissão para: {permissao.replace("_", " ")}'
                    )
                    raise PermissionDenied
                
                return view_func(request, *args, **kwargs)
                
            except PerfilUsuario.DoesNotExist:
                messages.error(request, 'Usuário sem perfil de acesso configurado.')
                return redirect('dashboard:index')
        
        return _wrapped_view
    return decorator


def representante_legal_required(view_func):
    """Shortcut decorator para Representante Legal apenas."""
    return require_perfil(PerfilAcesso.REPRESENTANTE_LEGAL)(view_func)


def representante_delegado_required(view_func):
    """Shortcut decorator para Representante Delegado ou superior."""
    return require_perfil(
        PerfilAcesso.REPRESENTANTE_LEGAL,
        PerfilAcesso.REPRESENTANTE_DELEGADO
    )(view_func)


# Mixins para Class-Based Views

class PerfilRequiredMixin(View):
    """
    Mixin para views baseadas em classe que requer perfis específicos.
    
    Usage:
        class MinhaView(PerfilRequiredMixin, TemplateView):
            perfis_permitidos = [PerfilAcesso.REPRESENTANTE_LEGAL]
            template_name = 'minha_template.html'
    """
    perfis_permitidos = []
    permission_denied_message = 'Você não tem permissão para acessar esta página.'
    redirect_url = 'dashboard:index'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('autenticacao:login')
        
        try:
            perfil = request.user.perfil
            
            # Verifica se o perfil está ativo
            if not perfil.ativo:
                messages.error(request, 'Seu perfil de acesso está desativado.')
                return redirect(self.redirect_url)
            
            # Verifica se o perfil está expirado
            if perfil.data_expiracao:
                from django.utils import timezone
                if timezone.now().date() > perfil.data_expiracao:
                    messages.error(request, 'Seu perfil de acesso expirou.')
                    return redirect(self.redirect_url)
            
            # Verifica se o perfil está na lista de permitidos
            if perfil.perfil not in self.perfis_permitidos:
                messages.error(request, self.permission_denied_message)
                raise PermissionDenied
            
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Usuário sem perfil de acesso configurado.')
            return redirect(self.redirect_url)
        
        return super().dispatch(request, *args, **kwargs)


class PermissaoRequiredMixin(View):
    """
    Mixin para views baseadas em classe que requer permissão específica.
    
    Usage:
        class EditarProdutoView(PermissaoRequiredMixin, UpdateView):
            permissao_requerida = 'editar_produtos'
            model = Produto
    """
    permissao_requerida = None
    permission_denied_message = 'Você não tem permissão para acessar esta página.'
    redirect_url = 'dashboard:index'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('autenticacao:login')
        
        if not self.permissao_requerida:
            raise ValueError('permissao_requerida não foi definida')
        
        try:
            perfil = request.user.perfil
            
            if not perfil.tem_permissao(self.permissao_requerida):
                messages.error(request, self.permission_denied_message)
                raise PermissionDenied
            
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Usuário sem perfil de acesso configurado.')
            return redirect(self.redirect_url)
        
        return super().dispatch(request, *args, **kwargs)


class RepresentanteLegalMixin(PerfilRequiredMixin):
    """Mixin para views que requerem Representante Legal."""
    perfis_permitidos = [PerfilAcesso.REPRESENTANTE_LEGAL]
    permission_denied_message = 'Esta funcionalidade está disponível apenas para Representante Legal.'


class RepresentanteDelegadoMixin(PerfilRequiredMixin):
    """Mixin para views que requerem Representante Delegado ou superior."""
    perfis_permitidos = [PerfilAcesso.REPRESENTANTE_LEGAL, PerfilAcesso.REPRESENTANTE_DELEGADO]
    permission_denied_message = 'Esta funcionalidade requer perfil de Representante.'


# Template tags helpers (para usar em templates)

def user_tem_perfil(user, perfil):
    """
    Verifica se o usuário tem um perfil específico.
    
    Usage em template:
        {% if user|user_tem_perfil:'REPR_LEGAL' %}
    """
    try:
        return user.perfil.perfil == perfil and user.perfil.ativo
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


def user_tem_permissao(user, permissao):
    """
    Verifica se o usuário tem uma permissão específica.
    
    Usage em template:
        {% if user|user_tem_permissao:'editar_produtos' %}
    """
    try:
        return user.perfil.tem_permissao(permissao)
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


def user_is_representante_legal(user):
    """Verifica se o usuário é Representante Legal."""
    try:
        return user.perfil.is_representante_legal()
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


def user_is_representante(user):
    """Verifica se o usuário é Representante (Legal ou Delegado)."""
    try:
        perfil = user.perfil
        return (perfil.is_representante_legal() or perfil.is_representante_delegado())
    except (AttributeError, PerfilUsuario.DoesNotExist):
        return False


# ============================================================================
# REST FRAMEWORK PERMISSIONS
# ============================================================================

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão que permite leitura para todos autenticados,
    mas apenas admin pode criar/editar/deletar.
    """
    
    def has_permission(self, request, view):
        # Leitura permitida para autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Escrita apenas para admin/staff
        return request.user and request.user.is_staff


class IsStaffUser(permissions.BasePermission):
    """
    Permissão que exige usuário staff (admin).
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAdminUser(permissions.BasePermission):
    """
    Permissão que exige usuário admin (is_staff).
    Alias para IsStaffUser para consistência de nomenclatura.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permissão que permite acesso total para admin,
    ou apenas para o próprio usuário (owner).
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin tem acesso total
        if request.user.is_staff:
            return True
        
        # Usuário pode acessar apenas seus próprios dados
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsRepresentanteLegal(permissions.BasePermission):
    """
    Permissão que exige perfil de Representante Legal.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'perfil'):
            return False
        
        return request.user.perfil.is_representante_legal()


class IsRepresentanteOrDelegado(permissions.BasePermission):
    """
    Permissão que exige perfil de Representante Legal ou Delegado.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'perfil'):
            return False
        
        perfil = request.user.perfil
        return perfil.is_representante_legal() or perfil.is_representante_delegado()


class CanManageProducts(permissions.BasePermission):
    """
    Permissão para gerenciar produtos.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Leitura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escrita apenas para quem pode editar produtos
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.pode_editar_produtos()
        
        # Fallback para staff
        return request.user.is_staff


class CanApproveMovements(permissions.BasePermission):
    """
    Permissão para aprovar movimentações.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'perfil'):
            return request.user.perfil.pode_aprovar_movimentacoes()
        
        return request.user.is_staff
