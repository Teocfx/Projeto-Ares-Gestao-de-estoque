"""
URLs para o módulo de busca.
"""
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search, name='search'),
]
