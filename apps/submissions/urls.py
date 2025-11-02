
"""
URL configuration for submissions app
"""
from django.urls import path
from apps.submissions import views

app_name = 'submissions'

urlpatterns = [
    path('', views.submission_list, name='submission_list'),
    path('create/', views.submission_create, name='submission_create'),
    path('<int:pk>/', views.submission_detail, name='submission_detail'),
    path('<int:pk>/edit/', views.submission_edit, name='submission_edit'),
    path('<int:pk>/delete/', views.submission_delete, name='submission_delete'),
    path('export/csv/', views.export_submissions_csv, name='export_submissions_csv'),
]
