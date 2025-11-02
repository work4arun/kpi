
"""
URL configuration for notifications app
"""
from django.urls import path
from apps.notifications import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/', views.notification_detail, name='notification_detail'),
    path('<int:pk>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
]
