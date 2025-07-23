"""
SLA Metrics models for tracking service performance and compliance.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class ServiceType(models.Model):
    """Service types for categorizing SLA metrics."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """Individual services being monitored for SLA compliance."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='services')
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # SLA Targets
    availability_target = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Target availability percentage (e.g., 99.9)"
    )
    response_time_target = models.PositiveIntegerField(
        help_text="Target response time in milliseconds"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'service_type']
    
    def __str__(self):
        return f"{self.name} ({self.service_type.name})"
    
    @property
    def current_availability(self):
        """Calculate current availability from recent metrics."""
        recent_metrics = self.metrics.filter(
            timestamp__gte=timezone.now() - timezone.timedelta(days=30)
        )
        if not recent_metrics.exists():
            return None
        
        total_uptime = sum(m.uptime_seconds for m in recent_metrics)
        total_time = recent_metrics.count() * 3600  # Assuming hourly metrics
        return (total_uptime / total_time) * 100 if total_time > 0 else 0


class SLAMetric(models.Model):
    """Individual SLA metric measurements."""
    METRIC_TYPES = [
        ('availability', 'Availability'),
        ('response_time', 'Response Time'),
        ('throughput', 'Throughput'),
        ('error_rate', 'Error Rate'),
        ('custom', 'Custom Metric'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='metrics')
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    timestamp = models.DateTimeField()
    
    # Metric values
    value = models.DecimalField(max_digits=15, decimal_places=4)
    unit = models.CharField(max_length=50, default='')
    
    # Additional context
    uptime_seconds = models.PositiveIntegerField(default=0)
    downtime_seconds = models.PositiveIntegerField(default=0)
    total_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    
    # Metadata
    source = models.CharField(max_length=100, help_text="Data source identifier")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['service', 'metric_type', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.service.name} - {self.metric_type} - {self.timestamp}"
    
    @property
    def is_meeting_sla(self):
        """Check if this metric meets the service's SLA target."""
        if self.metric_type == 'availability':
            return self.value >= self.service.availability_target
        elif self.metric_type == 'response_time':
            return self.value <= self.service.response_time_target
        return None


class SLAIncident(models.Model):
    """Track SLA violations and incidents."""
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='incidents')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Incident details
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    
    # Timing
    started_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Impact
    affected_users = models.PositiveIntegerField(default=0)
    revenue_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.service.name} - {self.title}"
    
    @property
    def duration(self):
        """Calculate incident duration."""
        end_time = self.resolved_at or timezone.now()
        return end_time - self.started_at
    
    @property
    def is_active(self):
        """Check if incident is still active."""
        return self.status in ['open', 'investigating']


class SLAReport(models.Model):
    """Generated SLA reports for services."""
    REPORT_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    
    # Report period
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Calculated metrics
    availability_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    average_response_time = models.DecimalField(max_digits=10, decimal_places=2)
    total_incidents = models.PositiveIntegerField(default=0)
    total_downtime_minutes = models.PositiveIntegerField(default=0)
    
    # SLA compliance
    sla_met = models.BooleanField()
    sla_breach_minutes = models.PositiveIntegerField(default=0)
    
    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-period_start']
        unique_together = ['service', 'report_type', 'period_start']
    
    def __str__(self):
        return f"{self.service.name} - {self.report_type} - {self.period_start.date()}"
