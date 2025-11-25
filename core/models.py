"""
Modelos core para o Sistema de Gestão de Estoque.

Este módulo contém modelos base e configurações compartilhadas.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


class TimeStampedModel(models.Model):
    """
    Model abstrato que adiciona campos de timestamp automáticos.
    Todas as models de negócio devem herdar deste model.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserTrackingModel(TimeStampedModel):
    """
    Model abstrato que adiciona rastreamento de usuário além dos timestamps.
    Útil para auditoria de criação e modificação.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        verbose_name="Criado por"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        verbose_name="Atualizado por"
    )

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Model abstrato que implementa soft delete.
    Ao invés de deletar registros, apenas marca como inativo.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para desativar este registro ao invés de excluí-lo"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Deletado em"
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca o registro como inativo."""
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura um registro soft-deleted."""
        self.is_active = True
        self.deleted_at = None
        self.save()


@register_setting(icon="site")
class SiteSettings(BaseSiteSetting):
    """Configurações gerais do site."""

    title_suffix = models.CharField(
        verbose_name="Título do Site",
        max_length=255,
        help_text="Título do site utilizado como sufixo. Ex.: ' | Sistema ARES'",
        default="Sistema ARES - Gestão de Estoque",
    )

    menu_max_levels = models.PositiveIntegerField(
        verbose_name="Níveis máximos do menu",
        default=2,
        help_text="Define até quantos níveis de páginas o menu principal irá exibir. (Máximo: 3)"
    )

    panels = [
        FieldPanel("title_suffix"),
        MultiFieldPanel(
            [
                FieldPanel("menu_max_levels"),
            ],
            heading="Menu do Site"
        ),
    ]

    def clean(self):
        super().clean()
        if self.menu_max_levels > 3:
            raise ValidationError({
                "menu_max_levels": "O número máximo de níveis permitido para o menu é 3."
            })

    class Meta:
        verbose_name = "Configurações do Site"


@register_setting(icon="link")
class ApiSettings(BaseSiteSetting):
    """Configurações de API para integrações externas."""
    
    api_habilitada = models.BooleanField(
        verbose_name="Habilitar Integração via API",
        default=False,
        help_text="Marque para ativar a integração com APIs externas."
    )
    
    api_url = models.URLField(
        verbose_name="URL da API Externa",
        blank=True,
        help_text="URL base da API externa"
    )
    
    api_token = models.CharField(
        max_length=255,
        verbose_name="Token da API",
        blank=True,
        help_text="Token para autenticação na API externa"
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("api_habilitada"),
                FieldPanel("api_url"),
                FieldPanel("api_token"),
            ],
            heading="Integração de API Externa"
        ),
    ]

    def clean(self):
        super().clean()
        if self.api_habilitada and not self.api_url:
            raise ValidationError({
                "api_url": "A URL da API é obrigatória quando a integração está habilitada."
            })

    class Meta:
        verbose_name = "Configurações de API"


class PerfilAcesso(models.TextChoices):
    """
    Perfis de acesso hierárquicos do sistema.
    Baseado no modelo do Itaú Empresas com 3 níveis de permissão.
    """
    REPRESENTANTE_LEGAL = 'REPR_LEGAL', 'Representante Legal'
    REPRESENTANTE_DELEGADO = 'REPR_DELEGADO', 'Representante Delegado'
    OPERADOR = 'OPERADOR', 'Operador'


class PerfilUsuario(TimeStampedModel):
    """
    Perfil de acesso do usuário no sistema.
    
    Hierarquia de Permissões:
    1. Representante Legal - Acesso total, pode gerenciar tudo
    2. Representante Delegado - Acesso administrativo limitado
    3. Operador - Acesso operacional básico
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuário"
    )
    
    perfil = models.CharField(
        max_length=20,
        choices=PerfilAcesso.choices,
        default=PerfilAcesso.OPERADOR,
        verbose_name="Perfil de Acesso"
    )
    
    # Representante Legal que autorizou este usuário
    autorizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_autorizados',
        verbose_name="Autorizado por",
        help_text="Representante Legal que autorizou este acesso"
    )
    
    # Permissões customizadas (sobrescreve permissões padrão do perfil)
    permissoes_customizadas = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Permissões Customizadas",
        help_text="Permissões específicas além das do perfil padrão"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para desativar o acesso do usuário"
    )
    
    data_expiracao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Expiração",
        help_text="Data em que o acesso expira (deixe em branco para nunca expirar)"
    )
    
    observacoes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Observações sobre o perfil do usuário"
    )

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['perfil', 'ativo']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_perfil_display()}"

    def clean(self):
        """Validações customizadas."""
        super().clean()
        
        # Apenas Representante Legal pode autorizar outros usuários
        if self.autorizado_por and not hasattr(self.autorizado_por, 'perfil'):
            raise ValidationError({
                'autorizado_por': 'Usuário autorizador deve ter um perfil configurado.'
            })
        
        if self.autorizado_por and hasattr(self.autorizado_por, 'perfil'):
            if self.autorizado_por.perfil.perfil != PerfilAcesso.REPRESENTANTE_LEGAL:
                raise ValidationError({
                    'autorizado_por': 'Apenas Representante Legal pode autorizar outros usuários.'
                })

    def is_representante_legal(self):
        """Verifica se é Representante Legal."""
        return self.perfil == PerfilAcesso.REPRESENTANTE_LEGAL and self.ativo

    def is_representante_delegado(self):
        """Verifica se é Representante Delegado."""
        return self.perfil == PerfilAcesso.REPRESENTANTE_DELEGADO and self.ativo

    def is_operador(self):
        """Verifica se é Operador."""
        return self.perfil == PerfilAcesso.OPERADOR and self.ativo

    def pode_gerenciar_usuarios(self):
        """Verifica se pode gerenciar outros usuários."""
        return self.is_representante_legal()

    def pode_aprovar_movimentacoes(self):
        """Verifica se pode aprovar movimentações."""
        return self.is_representante_legal() or self.is_representante_delegado()

    def pode_editar_produtos(self):
        """Verifica se pode editar produtos."""
        return self.is_representante_legal() or self.is_representante_delegado()

    def pode_visualizar_relatorios(self):
        """Verifica se pode visualizar relatórios."""
        return self.ativo  # Todos os perfis ativos podem visualizar

    def pode_gerar_relatorios(self):
        """Verifica se pode gerar relatórios."""
        return self.is_representante_legal() or self.is_representante_delegado()

    @staticmethod
    def get_permissoes_padrao(perfil):
        """
        Retorna permissões padrão para cada perfil.
        
        Args:
            perfil: Valor do enum PerfilAcesso
            
        Returns:
            dict: Dicionário com permissões booleanas
        """
        permissoes = {
            PerfilAcesso.REPRESENTANTE_LEGAL: {
                'gerenciar_usuarios': True,
                'aprovar_movimentacoes': True,
                'editar_produtos': True,
                'visualizar_relatorios': True,
                'gerar_relatorios': True,
                'alterar_configuracoes': True,
                'visualizar_logs': True,
                'excluir_registros': True,
            },
            PerfilAcesso.REPRESENTANTE_DELEGADO: {
                'gerenciar_usuarios': False,
                'aprovar_movimentacoes': True,
                'editar_produtos': True,
                'visualizar_relatorios': True,
                'gerar_relatorios': True,
                'alterar_configuracoes': False,
                'visualizar_logs': True,
                'excluir_registros': False,
            },
            PerfilAcesso.OPERADOR: {
                'gerenciar_usuarios': False,
                'aprovar_movimentacoes': False,
                'editar_produtos': False,
                'visualizar_relatorios': True,
                'gerar_relatorios': False,
                'alterar_configuracoes': False,
                'visualizar_logs': False,
                'excluir_registros': False,
            }
        }
        return permissoes.get(perfil, {})

    def tem_permissao(self, permissao):
        """
        Verifica se o usuário tem uma permissão específica.
        
        Args:
            permissao: String com nome da permissão
            
        Returns:
            bool: True se tem permissão, False caso contrário
        """
        if not self.ativo:
            return False
        
        # Verifica se há expiração configurada
        if self.data_expiracao:
            from django.utils import timezone
            if timezone.now().date() > self.data_expiracao:
                return False
        
        # Verifica permissões customizadas primeiro
        if permissao in self.permissoes_customizadas:
            return self.permissoes_customizadas[permissao]
        
        # Usa permissões padrão do perfil
        permissoes_padrao = self.get_permissoes_padrao(self.perfil)
        return permissoes_padrao.get(permissao, False)


class TipoAcaoAuditoria(models.TextChoices):
    """Tipos de ações que podem ser auditadas."""
    CREATE = 'CREATE', 'Criar'
    UPDATE = 'UPDATE', 'Atualizar'
    DELETE = 'DELETE', 'Excluir'
    VIEW = 'VIEW', 'Visualizar'
    LOGIN = 'LOGIN', 'Login'
    LOGOUT = 'LOGOUT', 'Logout'
    PERMISSION_CHANGE = 'PERM_CHANGE', 'Mudança de Permissão'
    EXPORT = 'EXPORT', 'Exportar'
    IMPORT = 'IMPORT', 'Importar'
    APPROVE = 'APPROVE', 'Aprovar'
    REJECT = 'REJECT', 'Rejeitar'
    OTHER = 'OTHER', 'Outro'


class NivelSeveridade(models.TextChoices):
    """Nível de severidade da ação auditada."""
    LOW = 'LOW', 'Baixo'
    MEDIUM = 'MEDIUM', 'Médio'
    HIGH = 'HIGH', 'Alto'
    CRITICAL = 'CRITICAL', 'Crítico'


class AuditLog(models.Model):
    """
    Log de auditoria para rastreamento de ações no sistema.
    
    Registra todas as ações importantes para compliance e segurança.
    """
    # Quem fez a ação
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name="Usuário"
    )
    
    # Quando foi feita
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data/Hora",
        db_index=True
    )
    
    # Tipo de ação
    action = models.CharField(
        max_length=20,
        choices=TipoAcaoAuditoria.choices,
        verbose_name="Ação",
        db_index=True
    )
    
    # Nível de severidade
    severity = models.CharField(
        max_length=10,
        choices=NivelSeveridade.choices,
        default=NivelSeveridade.LOW,
        verbose_name="Severidade",
        db_index=True
    )
    
    # Objeto afetado (usando ContentType para flexibilidade)
    from django.contrib.contenttypes.fields import GenericForeignKey
    from django.contrib.contenttypes.models import ContentType
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Objeto"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID do Objeto"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Representação em string do objeto (para caso ele seja deletado)
    object_repr = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Representação do Objeto"
    )
    
    # Descrição da ação
    description = models.TextField(
        verbose_name="Descrição"
    )
    
    # Dados adicionais em JSON
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Metadados",
        help_text="Dados adicionais sobre a ação (JSON)"
    )
    
    # Informações de requisição
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Endereço IP"
    )
    
    user_agent = models.TextField(
        blank=True,
        verbose_name="User Agent"
    )
    
    # Mudanças (antes e depois)
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Mudanças",
        help_text="Valores antes e depois da alteração"
    )

    class Meta:
        verbose_name = "Log de Auditoria"
        verbose_name_plural = "Logs de Auditoria"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'user']),
            models.Index(fields=['action', 'severity']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Sistema"
        return f"{user_name} - {self.get_action_display()} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    @classmethod
    def log_action(cls, user, action, description, content_object=None, 
                   severity=NivelSeveridade.LOW, metadata=None, changes=None,
                   request=None):
        """
        Método helper para criar logs de auditoria.
        
        Args:
            user: Usuário que realizou a ação
            action: Tipo de ação (TipoAcaoAuditoria)
            description: Descrição da ação
            content_object: Objeto afetado (opcional)
            severity: Nível de severidade (opcional)
            metadata: Metadados adicionais (opcional)
            changes: Mudanças realizadas (opcional)
            request: Request HTTP (opcional, para IP e User-Agent)
        
        Returns:
            AuditLog: Instância criada
        """
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'severity': severity,
            'metadata': metadata or {},
            'changes': changes or {},
        }
        
        # Se tem objeto relacionado
        if content_object:
            log_data['content_object'] = content_object
            log_data['object_repr'] = str(content_object)
        
        # Se tem request, captura IP e User-Agent
        if request:
            log_data['ip_address'] = cls.get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return cls.objects.create(**log_data)

    @staticmethod
    def get_client_ip(request):
        """Obtém o IP real do cliente, considerando proxies."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_severity_badge_class(self):
        """Retorna classe CSS do badge de severidade."""
        badges = {
            NivelSeveridade.LOW: 'bg-info',
            NivelSeveridade.MEDIUM: 'bg-warning',
            NivelSeveridade.HIGH: 'bg-danger',
            NivelSeveridade.CRITICAL: 'bg-dark',
        }
        return badges.get(self.severity, 'bg-secondary')


# Exportar modelos base para uso em outros apps
__all__ = [
    'TimeStampedModel', 
    'UserTrackingModel', 
    'SoftDeleteModel', 
    'SiteSettings', 
    'ApiSettings',
    'PerfilAcesso',
    'PerfilUsuario',
    'TipoAcaoAuditoria',
    'NivelSeveridade',
    'AuditLog',
]
