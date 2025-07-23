"""
URL configuration for SLA Metrics API.
"""

from django.urls import path
from . import api_views

app_name = 'sla_metrics'

urlpatterns = [
    # Service Types
    path('service-types/', api_views.ServiceTypeListCreateView.as_view(), name='servicetype-list'),
    path('service-types/<int:pk>/', api_views.ServiceTypeRetrieveUpdateDestroyView.as_view(), name='servicetype-detail'),
    
    # Services
    path('services/', api_views.ServiceListCreateView.as_view(), name='service-list'),
    path('services/<uuid:pk>/', api_views.ServiceRetrieveUpdateDestroyView.as_view(), name='service-detail'),
    
    # SLA Metrics
    path('metrics/', api_views.SLAMetricListCreateView.as_view(), name='slametric-list'),
    path('metrics/<uuid:pk>/', api_views.SLAMetricRetrieveUpdateDestroyView.as_view(), name='slametric-detail'),
    
    # SLA Incidents
    path('incidents/', api_views.SLAIncidentListCreateView.as_view(), name='slaincident-list'),
    path('incidents/<uuid:pk>/', api_views.SLAIncidentRetrieveUpdateDestroyView.as_view(), name='slaincident-detail'),
    
    # SLA Reports
    path('reports/', api_views.SLAReportListCreateView.as_view(), name='slareport-list'),
    path('reports/<uuid:pk>/', api_views.SLAReportRetrieveUpdateDestroyView.as_view(), name='slareport-detail'),
    
    # Dashboard and Analytics
    path('dashboard/stats/', api_views.dashboard_stats, name='dashboard-stats'),
    path('services/<uuid:service_id>/metrics/chart/', api_views.service_metrics_chart, name='service-metrics-chart'),
    path('services/<uuid:service_id>/availability/', api_views.service_availability_summary, name='service-availability'),
]