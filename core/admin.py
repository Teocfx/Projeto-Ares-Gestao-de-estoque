"""
Configuração do Django Admin para o app Core.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils import timezone
from .models import PerfilUsuario, PerfilAcesso, AuditLog, TipoAcaoAuditoria


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Admin customizado para Perfis de Usuário."""
    
    list_display = [
        'user_info',
        'perfil_badge',
        'status_badge',
        'autorizado_por',
        'data_expiracao',
        'created_at'
    ]
    
    list_filter = [
        'perfil',
        'ativo',
        'created_at',
        ('data_expiracao', admin.EmptyFieldListFilter),
    ]
    
    search_fields = [
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__email',
        'observacoes'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'permissoes_padrao_display'
    ]
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Perfil de Acesso', {
            'fields': (
                'perfil',
                'ativo',
                'data_expiracao',
                'autorizado_por',
            )
        }),
        ('Permissões', {
            'fields': (
                'permissoes_padrao_display',
                'permissoes_customizadas',
            ),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    autocomplete_fields = ['user', 'autorizado_por']
    
    def user_info(self, obj):
        """Exibe informações do usuário."""
        user = obj.user
        name = user.get_full_name() or user.username
        email = user.email or 'Sem email'
        return format_html(
            '<strong>{}</strong><br><small class="text-muted">{}</small>',
            name,
            email
        )
    user_info.short_description = 'Usuário'
    
    def perfil_badge(self, obj):
        """Exibe badge colorido do perfil."""
        colors = {
            PerfilAcesso.REPRESENTANTE_LEGAL: '#dc3545',
            PerfilAcesso.REPRESENTANTE_DELEGADO: '#ffc107',
            PerfilAcesso.OPERADOR: '#0dcaf0',
        }
        color = colors.get(obj.perfil, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_perfil_display()
        )
    perfil_badge.short_description = 'Perfil'
    
    def status_badge(self, obj):
        """Exibe status do perfil."""
        if not obj.ativo:
            return format_html(
                '<span style="color: #dc3545;"><i class="bi bi-x-circle"></i> Desativado</span>'
            )
        
        if obj.data_expiracao and timezone.now().date() > obj.data_expiracao:
            return format_html(
                '<span style="color: #ffc107;"><i class="bi bi-exclamation-triangle"></i> Expirado</span>'
            )
        
        return format_html(
            '<span style="color: #198754;"><i class="bi bi-check-circle"></i> Ativo</span>'
        )
    status_badge.short_description = 'Status'
    
    def permissoes_padrao_display(self, obj):
        """Exibe as permissões padrão do perfil."""
        if not obj.perfil:
            return "-"
        
        permissoes = PerfilUsuario.get_permissoes_padrao(obj.perfil)
        html = '<ul style="margin: 0; padding-left: 20px;">'
        
        for perm, tem_acesso in permissoes.items():
            icon = '✅' if tem_acesso else '❌'
            perm_label = perm.replace('_', ' ').title()
            html += f'<li>{icon} {perm_label}</li>'
        
        html += '</ul>'
        return format_html(html)
    permissoes_padrao_display.short_description = 'Permissões Padrão do Perfil'
    
    def get_queryset(self, request):
        """Otimiza queries."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'autorizado_por')
    
    def save_model(self, request, obj, form, change):
        """Validações adicionais ao salvar."""
        # Se está criando um novo perfil, define o autorizador como o usuário atual
        if not change and not obj.autorizado_por:
            if hasattr(request.user, 'perfil'):
                if request.user.perfil.is_representante_legal():
                    obj.autorizado_por = request.user
        
        super().save_model(request, obj, form, change)


# Inline para adicionar Perfil na tela de edição de User
class PerfilUsuarioInline(admin.StackedInline):
    """Inline para gerenciar perfil na tela de usuário."""
    model = PerfilUsuario
    fk_name = 'user'  # Especifica qual ForeignKey usar
    can_delete = False
    verbose_name = 'Perfil de Acesso'
    verbose_name_plural = 'Perfil de Acesso'
    
    fieldsets = (
        (None, {
            'fields': (
                'perfil',
                'ativo',
                'data_expiracao',
                'autorizado_por',
                'observacoes',
            )
        }),
    )
    
    autocomplete_fields = ['autorizado_por']


# Extende o UserAdmin para incluir o Perfil
class UserAdmin(BaseUserAdmin):
    """User Admin customizado com Perfil integrado."""
    inlines = (PerfilUsuarioInline,)
    
    list_display = BaseUserAdmin.list_display + ('perfil_info', 'last_login')
    
    def perfil_info(self, obj):
        """Exibe informação do perfil na lista de usuários."""
        try:
            perfil = obj.perfil
            colors = {
                PerfilAcesso.REPRESENTANTE_LEGAL: '#dc3545',
                PerfilAcesso.REPRESENTANTE_DELEGADO: '#ffc107',
                PerfilAcesso.OPERADOR: '#0dcaf0',
            }
            color = colors.get(perfil.perfil, '#6c757d')
            
            if not perfil.ativo:
                return format_html(
                    '<span style="color: #dc3545; text-decoration: line-through;">{}</span>',
                    perfil.get_perfil_display()
                )
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                perfil.get_perfil_display()
            )
        except PerfilUsuario.DoesNotExist:
            return format_html(
                '<span style="color: #6c757d; font-style: italic;">Sem perfil</span>'
            )
    perfil_info.short_description = 'Perfil'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para Logs de Auditoria - Somente leitura."""
    
    list_display = [
        'timestamp',
        'user_info',
        'action_badge',
        'severity_badge',
        'description_short',
        'ip_address'
    ]
    
    list_filter = [
        'action',
        'severity',
        'timestamp',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'description',
        'user__username',
        'user__first_name',
        'user__last_name',
        'ip_address',
        'object_repr'
    ]
    
    readonly_fields = [
        'timestamp',
        'user',
        'action',
        'severity',
        'content_type',
        'object_id',
        'object_repr',
        'description',
        'metadata_display',
        'changes_display',
        'ip_address',
        'user_agent_display',
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('timestamp', 'user', 'ip_address')
        }),
        ('Ação', {
            'fields': ('action', 'severity', 'description')
        }),
        ('Objeto Afetado', {
            'fields': ('content_type', 'object_id', 'object_repr'),
            'classes': ('collapse',)
        }),
        ('Detalhes', {
            'fields': ('changes_display', 'metadata_display'),
            'classes': ('collapse',)
        }),
        ('Request', {
            'fields': ('user_agent_display',),
            'classes': ('collapse',)
        }),
    )
    
    # Desabilita adição, edição e exclusão
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Apenas superuser pode excluir logs
        return request.user.is_superuser
    
    def user_info(self, obj):
        """Exibe informações do usuário."""
        if not obj.user:
            return format_html('<span class="text-muted">Sistema</span>')
        
        user = obj.user
        name = user.get_full_name() or user.username
        
        return format_html(
            '<strong>{}</strong><br><small class="text-muted">{}</small>',
            name,
            user.username
        )
    user_info.short_description = 'Usuário'
    
    def action_badge(self, obj):
        """Badge colorido para ação."""
        colors = {
            TipoAcaoAuditoria.CREATE: '#198754',
            TipoAcaoAuditoria.UPDATE: '#0dcaf0',
            TipoAcaoAuditoria.DELETE: '#dc3545',
            TipoAcaoAuditoria.LOGIN: '#0d6efd',
            TipoAcaoAuditoria.LOGOUT: '#6c757d',
            TipoAcaoAuditoria.PERMISSION_CHANGE: '#fd7e14',
            TipoAcaoAuditoria.EXPORT: '#6610f2',
            TipoAcaoAuditoria.IMPORT: '#d63384',
        }
        
        color = colors.get(obj.action, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Ação'
    
    def severity_badge(self, obj):
        """Badge de severidade."""
        return format_html(
            '<span class="badge {}">{}</span>',
            obj.get_severity_badge_class(),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidade'
    
    def description_short(self, obj):
        """Descrição truncada."""
        if len(obj.description) > 100:
            return obj.description[:100] + '...'
        return obj.description
    description_short.short_description = 'Descrição'
    
    def metadata_display(self, obj):
        """Exibe metadados formatados."""
        if not obj.metadata:
            return '-'
        
        import json
        return format_html(
            '<pre style="margin: 0; padding: 10px; background: #f8f9fa; border-radius: 4px; max-height: 300px; overflow: auto;">{}</pre>',
            json.dumps(obj.metadata, indent=2, ensure_ascii=False)
        )
    metadata_display.short_description = 'Metadados'
    
    def changes_display(self, obj):
        """Exibe mudanças formatadas."""
        if not obj.changes:
            return '-'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background: #f8f9fa;"><th style="padding: 8px; text-align: left;">Campo</th><th style="padding: 8px; text-align: left;">Antes</th><th style="padding: 8px; text-align: left;">Depois</th></tr>'
        
        for field, change in obj.changes.items():
            html += f'''
            <tr style="border-bottom: 1px solid #dee2e6;">
                <td style="padding: 8px;"><strong>{field}</strong></td>
                <td style="padding: 8px; color: #dc3545;">{change.get('old', '-')}</td>
                <td style="padding: 8px; color: #198754;">{change.get('new', '-')}</td>
            </tr>
            '''
        
        html += '</table>'
        return format_html(html)
    changes_display.short_description = 'Mudanças'
    
    def user_agent_display(self, obj):
        """Exibe user agent truncado."""
        if not obj.user_agent:
            return '-'
        
        if len(obj.user_agent) > 200:
            return obj.user_agent[:200] + '...'
        return obj.user_agent
    user_agent_display.short_description = 'User Agent'
    
    def get_queryset(self, request):
        """Otimiza queries."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'content_type')
