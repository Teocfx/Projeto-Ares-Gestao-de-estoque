from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView
from django.views.generic import RedirectView

from django.shortcuts import render
from . import views

handler403 = 'core.handlers.permission_denied_handler'
handler404 = 'siteares.views.erro_404'
handler500 = 'siteares.views.erro_500'

urlpatterns = [
    # Django Admin
    path("django-admin/", admin.site.urls),
    
    # Wagtail CMS
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    re_path(
        r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
        ServeView.as_view(),
        name="wagtailimages_serve",
    ),
    
    # Apps de Gestão de Estoque ARES (área administrativa)
    path('dashboard/', include('dashboard.urls')),  # Dashboard em /dashboard/
    path('auth/', include('autenticacao.urls')),
    path('produtos/', include('produtos.urls')),
    path('movimentacoes/', include('movimentacoes.urls')),
    path('relatorios/', include('relatorios.urls')),
    path('search/', include('search.urls')),
    
    # Redirect raiz baseado em autenticação
    path('', views.home_redirect, name='home'),
    
    # Autenticação de Dois Fatores (2FA)
    path('2fa/', include('autenticacao_2fa.urls')),
    
    # Core URLs
    path("core/", include("core.urls")),
    
    # API REST v1
    path("api/v1/", include("siteares.api_urls", namespace="api-v1")),
    
    # Utilidades
    path("__reload__/", include("django_browser_reload.urls")),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "img/favicon.ico")),
    
    # Wagtail CMS pages (páginas institucionais)
    path("loja/", include(wagtail_urls)),  # Páginas Wagtail em /loja/
]

# SSO Login (se habilitado)
HABILITAR_SSO_LOGIN = getattr(settings, 'HABILITAR_SSO_LOGIN', False)
if HABILITAR_SSO_LOGIN:
    urlpatterns += [
        path("admin/manager/logout/", views.wagtail_logout_with_sso, name="wagtailadmin_logout"),
        path('admin/manager/login/', RedirectView.as_view(url='/admin/', permanent=True)),
        path("admin/", include("allauth.urls")),
    ]

# Static e Media files em desenvolvimento
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
def erro_500(request):
    return render(request, "500.html", status=500)

handler500 = erro_500