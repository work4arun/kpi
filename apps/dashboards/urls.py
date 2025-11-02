
"""
URL configuration for dashboards app
"""
from django.urls import path
from apps.dashboards import views

app_name = 'dashboards'

urlpatterns = [
    path('', views.dashboard_redirect, name='dashboard'),
]
