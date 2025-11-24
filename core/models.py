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


# Exportar modelos base para uso em outros apps
__all__ = ['TimeStampedModel', 'UserTrackingModel', 'SoftDeleteModel', 'SiteSettings', 'ApiSettings']
