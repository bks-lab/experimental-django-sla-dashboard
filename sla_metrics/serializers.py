"""
Django REST Framework serializers for SLA Metrics models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ServiceType, Service, SLAMetric, SLAIncident, SLAReport


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ServiceTypeSerializer(serializers.ModelSerializer):
    """Serializer for ServiceType model."""
    
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Service list views."""
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    current_availability = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'service_type_name', 'availability_target', 
            'response_time_target', 'is_active', 'owner_username', 
            'current_availability', 'created_at'
        ]


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Service model."""
    service_type = ServiceTypeSerializer(read_only=True)
    service_type_id = serializers.UUIDField(write_only=True)
    owner = UserSerializer(read_only=True)
    owner_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    current_availability = serializers.ReadOnlyField()
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'service_type', 'service_type_id',
            'owner', 'owner_id', 'availability_target', 'response_time_target',
            'is_active', 'current_availability', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SLAMetricSerializer(serializers.ModelSerializer):
    """Serializer for SLAMetric model."""
    service_name = serializers.CharField(source='service.name', read_only=True)
    is_meeting_sla = serializers.ReadOnlyField()
    
    class Meta:
        model = SLAMetric
        fields = [
            'id', 'service', 'service_name', 'metric_type', 'timestamp',
            'value', 'unit', 'uptime_seconds', 'downtime_seconds',
            'total_requests', 'failed_requests', 'source', 'notes',
            'is_meeting_sla', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SLAMetricCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating SLA metrics."""
    
    class Meta:
        model = SLAMetric
        fields = [
            'service', 'metric_type', 'timestamp', 'value', 'unit',
            'uptime_seconds', 'downtime_seconds', 'total_requests',
            'failed_requests', 'source', 'notes'
        ]


class SLAIncidentSerializer(serializers.ModelSerializer):
    """Serializer for SLAIncident model."""
    service_name = serializers.CharField(source='service.name', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True)
    duration = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = SLAIncident
        fields = [
            'id', 'service', 'service_name', 'title', 'description',
            'severity', 'status', 'started_at', 'resolved_at',
            'assigned_to', 'assigned_to_username', 'affected_users',
            'revenue_impact', 'duration', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SLAReportSerializer(serializers.ModelSerializer):
    """Serializer for SLAReport model."""
    service_name = serializers.CharField(source='service.name', read_only=True)
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    
    class Meta:
        model = SLAReport
        fields = [
            'id', 'service', 'service_name', 'report_type', 'period_start',
            'period_end', 'availability_percentage', 'average_response_time',
            'total_incidents', 'total_downtime_minutes', 'sla_met',
            'sla_breach_minutes', 'generated_by_username', 'generated_at'
        ]
        read_only_fields = ['id', 'generated_at']


class ServiceStatsSerializer(serializers.Serializer):
    """Serializer for service statistics."""
    service_id = serializers.UUIDField()
    service_name = serializers.CharField()
    current_availability = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    target_availability = serializers.DecimalField(max_digits=5, decimal_places=2)
    recent_incidents = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    sla_status = serializers.CharField()  # 'meeting', 'breach', 'unknown'