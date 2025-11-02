
"""
URL configuration for departments app
"""
from django.urls import path
from apps.departments import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list, name='department_list'),
]
