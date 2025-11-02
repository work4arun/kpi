
"""
URL configuration for KPI app
"""
from django.urls import path
from apps.kpi import views

app_name = 'kpi'

urlpatterns = [
    path('main-parameters/', views.main_parameter_list, name='main_parameter_list'),
    path('sub-parameters/', views.sub_parameter_list, name='sub_parameter_list'),
    path('cutoff-windows/', views.cutoff_window_list, name='cutoff_window_list'),
]
