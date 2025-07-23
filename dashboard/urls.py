"""
URL configuration for Dashboard API.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard view
    path('', views.DashboardView.as_view(), name='index'),
    
    # API endpoints for dashboard data
    path('api/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('api/availability-timeline/', views.availability_timeline, name='availability_timeline'),
    path('api/response-time-distribution/', views.response_time_distribution, name='response_time_distribution'),
    path('api/sla-compliance/', views.sla_compliance, name='sla_compliance'),
    path('api/recent-alerts/', views.recent_alerts, name='recent_alerts'),
    path('api/alerts/<uuid:alert_id>/acknowledge/', views.acknowledge_alert, name='acknowledge_alert'),
]