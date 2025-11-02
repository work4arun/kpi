
"""
URL configuration for RTC KPI System project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # App URLs
    path('', include('apps.common.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('departments/', include('apps.departments.urls')),
    path('kpi/', include('apps.kpi.urls')),
    path('submissions/', include('apps.submissions.urls')),
    path('reviews/', include('apps.reviews.urls')),
    path('dashboards/', include('apps.dashboards.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('forms/', include('apps.forms_builder.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "RTC KPI System Administration"
admin.site.site_title = "RTC KPI Admin"
admin.site.index_title = "Welcome to RTC KPI System"
