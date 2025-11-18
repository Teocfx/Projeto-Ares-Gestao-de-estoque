"""
URLs do app Autenticação.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'autenticacao'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('recuperar-senha/', views.recuperar_senha, name='recuperar_senha'),
]
