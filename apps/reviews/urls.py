
"""
URL configuration for reviews app
"""
from django.urls import path
from apps.reviews import views

app_name = 'reviews'

urlpatterns = [
    path('', views.review_list, name='review_list'),
    path('<int:pk>/', views.review_detail, name='review_detail'),
    path('<int:pk>/approve/', views.review_approve, name='review_approve'),
    path('<int:pk>/reject/', views.review_reject, name='review_reject'),
    path('<int:pk>/revision/', views.review_request_revision, name='review_revision'),
    path('dean/', views.dean_review_list, name='dean_review_list'),
    path('dean/faculty/<int:faculty_id>/approve/', views.dean_approve_faculty, name='dean_approve_faculty'),
]
