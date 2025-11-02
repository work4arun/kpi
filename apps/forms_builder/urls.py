
"""
URL configuration for forms builder app
"""
from django.urls import path
from apps.forms_builder import views

app_name = 'forms_builder'

urlpatterns = [
    path('', views.form_builder_index, name='index'),
]
