"""
Django admin configuration for SLA Metrics models.
"""

from django.contrib import admin
from .models import ServiceType, Service, SLAMetric, SLAIncident, SLAReport


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'availability_target', 'response_time_target', 'is_active', 'owner']
    list_filter = ['service_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    autocomplete_fields = ['owner']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'service_type', 'description', 'owner')
        }),
        ('SLA Targets', {
            'fields': ('availability_target', 'response_time_target')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(SLAMetric)
class SLAMetricAdmin(admin.ModelAdmin):
    list_display = ['service', 'metric_type', 'value', 'timestamp', 'is_meeting_sla', 'source']
    list_filter = ['metric_type', 'timestamp', 'service__service_type']
    search_fields = ['service__name', 'source']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('service', 'metric_type', 'timestamp', 'value', 'unit')
        }),
        ('Additional Metrics', {
            'fields': ('uptime_seconds', 'downtime_seconds', 'total_requests', 'failed_requests'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('source', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    def is_meeting_sla(self, obj):
        result = obj.is_meeting_sla
        if result is None:
            return '-'
        return '✅' if result else '❌'
    is_meeting_sla.short_description = 'Meeting SLA'


@admin.register(SLAIncident)
class SLAIncidentAdmin(admin.ModelAdmin):
    list_display = ['service', 'title', 'severity', 'status', 'started_at', 'duration', 'assigned_to']
    list_filter = ['severity', 'status', 'started_at', 'service__service_type']
    search_fields = ['title', 'description', 'service__name']
    ordering = ['-started_at']
    date_hierarchy = 'started_at'
    autocomplete_fields = ['assigned_to']
    
    fieldsets = (
        ('Incident Details', {
            'fields': ('service', 'title', 'description', 'severity', 'status')
        }),
        ('Timing', {
            'fields': ('started_at', 'resolved_at')
        }),
        ('Assignment & Impact', {
            'fields': ('assigned_to', 'affected_users', 'revenue_impact')
        }),
    )
    
    def duration(self, obj):
        return str(obj.duration).split('.')[0]  # Remove microseconds
    duration.short_description = 'Duration'


@admin.register(SLAReport)
class SLAReportAdmin(admin.ModelAdmin):
    list_display = ['service', 'report_type', 'period_start', 'availability_percentage', 'sla_met', 'generated_at']
    list_filter = ['report_type', 'sla_met', 'period_start', 'service__service_type']
    search_fields = ['service__name']
    ordering = ['-period_start']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('service', 'report_type', 'period_start', 'period_end')
        }),
        ('Metrics', {
            'fields': ('availability_percentage', 'average_response_time', 'total_incidents', 'total_downtime_minutes')
        }),
        ('SLA Compliance', {
            'fields': ('sla_met', 'sla_breach_minutes')
        }),
        ('Metadata', {
            'fields': ('generated_by',),
            'classes': ('collapse',)
        }),
    )
