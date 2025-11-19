"""
URLs para o módulo de busca.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
]
