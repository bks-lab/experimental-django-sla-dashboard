"""
Django REST Framework API views for SLA Metrics.
"""

from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Min, Max, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import ServiceType, Service, SLAMetric, SLAIncident, SLAReport
from .serializers import (
    ServiceTypeSerializer, ServiceListSerializer, ServiceDetailSerializer,
    SLAMetricSerializer, SLAMetricCreateSerializer, SLAIncidentSerializer,
    SLAReportSerializer, ServiceStatsSerializer
)


class ServiceTypeListCreateView(generics.ListCreateAPIView):
    """List all service types or create a new service type."""
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class ServiceTypeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service type."""
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer


class ServiceListCreateView(generics.ListCreateAPIView):
    """List all services or create a new service."""
    queryset = Service.objects.select_related('service_type', 'owner')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service_type', 'is_active', 'owner']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'availability_target']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ServiceDetailSerializer
        return ServiceListSerializer


class ServiceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a service."""
    queryset = Service.objects.select_related('service_type', 'owner')
    serializer_class = ServiceDetailSerializer


class SLAMetricListCreateView(generics.ListCreateAPIView):
    """List all SLA metrics or create new metrics."""
    queryset = SLAMetric.objects.select_related('service', 'service__service_type')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'metric_type', 'source']
    search_fields = ['service__name', 'source', 'notes']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SLAMetricCreateSerializer
        return SLAMetricSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset


class SLAMetricRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an SLA metric."""
    queryset = SLAMetric.objects.select_related('service')
    serializer_class = SLAMetricSerializer


class SLAIncidentListCreateView(generics.ListCreateAPIView):
    """List all SLA incidents or create new incidents."""
    queryset = SLAIncident.objects.select_related('service', 'assigned_to')
    serializer_class = SLAIncidentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'severity', 'status', 'assigned_to']
    search_fields = ['title', 'description', 'service__name']
    ordering_fields = ['started_at', 'severity', 'affected_users']
    ordering = ['-started_at']


class SLAIncidentRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an SLA incident."""
    queryset = SLAIncident.objects.select_related('service', 'assigned_to')
    serializer_class = SLAIncidentSerializer


class SLAReportListCreateView(generics.ListCreateAPIView):
    """List all SLA reports or create new reports."""
    queryset = SLAReport.objects.select_related('service', 'generated_by')
    serializer_class = SLAReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['service', 'report_type', 'sla_met']
    search_fields = ['service__name']
    ordering_fields = ['period_start', 'generated_at']
    ordering = ['-period_start']


class SLAReportRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an SLA report."""
    queryset = SLAReport.objects.select_related('service', 'generated_by')
    serializer_class = SLAReportSerializer


@api_view(['GET'])
def dashboard_stats(request):
    """Get dashboard statistics for all services."""
    services = Service.objects.filter(is_active=True).select_related('service_type')
    
    stats = []
    for service in services:
        # Get recent incidents (last 30 days)
        recent_incidents = SLAIncident.objects.filter(
            service=service,
            started_at__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        # Get active alerts (placeholder - would integrate with alerts app)
        active_alerts = 0  # This would query the alerts app
        
        # Determine SLA status
        current_availability = service.current_availability
        if current_availability is None:
            sla_status = 'unknown'
        elif current_availability >= service.availability_target:
            sla_status = 'meeting'
        else:
            sla_status = 'breach'
        
        stats.append({
            'service_id': service.id,
            'service_name': service.name,
            'current_availability': current_availability,
            'target_availability': service.availability_target,
            'recent_incidents': recent_incidents,
            'active_alerts': active_alerts,
            'sla_status': sla_status
        })
    
    serializer = ServiceStatsSerializer(stats, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def service_metrics_chart(request, service_id):
    """Get metrics data for charting a specific service."""
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get query parameters
    metric_type = request.query_params.get('metric_type', 'availability')
    days = int(request.query_params.get('days', 7))
    
    # Calculate date range
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get metrics
    metrics = SLAMetric.objects.filter(
        service=service,
        metric_type=metric_type,
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).order_by('timestamp')
    
    # Format data for charting
    chart_data = []
    for metric in metrics:
        chart_data.append({
            'timestamp': metric.timestamp,
            'value': float(metric.value),
            'unit': metric.unit
        })
    
    return Response({
        'service_name': service.name,
        'metric_type': metric_type,
        'period_days': days,
        'data': chart_data
    })


@api_view(['GET'])
def service_availability_summary(request, service_id):
    """Get availability summary for a specific service."""
    try:
        service = Service.objects.get(id=service_id)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get availability metrics
    availability_metrics = SLAMetric.objects.filter(
        service=service,
        metric_type='availability',
        timestamp__gte=start_date,
        timestamp__lte=end_date
    )
    
    if not availability_metrics.exists():
        return Response({
            'service_name': service.name,
            'period_days': days,
            'average_availability': None,
            'min_availability': None,
            'max_availability': None,
            'total_downtime_minutes': 0,
            'sla_target': float(service.availability_target),
            'sla_breach_count': 0
        })
    
    # Calculate statistics
    stats = availability_metrics.aggregate(
        avg_availability=Avg('value'),
        min_availability=Min('value'),
        max_availability=Max('value'),
        total_downtime=Sum('downtime_seconds')
    )
    
    # Count SLA breaches
    sla_breach_count = availability_metrics.filter(
        value__lt=service.availability_target
    ).count()
    
    return Response({
        'service_name': service.name,
        'period_days': days,
        'average_availability': float(stats['avg_availability']) if stats['avg_availability'] else None,
        'min_availability': float(stats['min_availability']) if stats['min_availability'] else None,
        'max_availability': float(stats['max_availability']) if stats['max_availability'] else None,
        'total_downtime_minutes': (stats['total_downtime'] or 0) // 60,
        'sla_target': float(service.availability_target),
        'sla_breach_count': sla_breach_count
    })