"""
URL configuration for sla_dashboard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/sla/', include('sla_metrics.urls')),
    path('api/v1/data-sources/', include('data_sources.urls')),
    path('api/v1/alerts/', include('alerts.urls')),
    path('api/v1/dashboard/', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
