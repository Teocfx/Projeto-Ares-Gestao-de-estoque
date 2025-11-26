"""
URLs para autenticacao_2fa.
"""
from django.urls import path
from . import views

app_name = 'autenticacao_2fa'

urlpatterns = [
    path('setup/', views.setup_2fa, name='setup_2fa'),
    path('verify/', views.verify_2fa, name='verify_2fa'),
    path('success/', views.success_2fa, name='success'),
    path('disable/', views.disable_2fa, name='disable_2fa'),
    path('status/', views.status_2fa, name='status'),
]
