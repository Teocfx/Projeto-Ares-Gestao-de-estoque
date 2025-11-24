"""
URLs do app Dashboard.
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/chart-data/', views.get_chart_data, name='chart_data'),
    path('api/filter-options/', views.get_filter_options, name='filter_options'),
]
