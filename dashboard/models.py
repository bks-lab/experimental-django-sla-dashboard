"""
Dashboard models for SLA dashboard visualization and user preferences.
"""

from django.db import models
from django.contrib.auth.models import User
from sla_metrics.models import Service
import uuid


class Dashboard(models.Model):
    """Custom dashboards for different users or teams."""
    DASHBOARD_TYPES = [
        ('overview', 'Overview'),
        ('service', 'Service Specific'),
        ('executive', 'Executive Summary'),
        ('operational', 'Operational'),
        ('custom', 'Custom'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    dashboard_type = models.CharField(max_length=15, choices=DASHBOARD_TYPES, default='custom')
    
    # Access control
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_dashboards')
    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_dashboards')
    is_public = models.BooleanField(default=False)
    
    # Configuration
    layout_config = models.JSONField(
        default=dict,
        help_text="Dashboard layout configuration (widgets, positions, etc.)"
    )
    refresh_interval = models.PositiveIntegerField(
        default=300,
        help_text="Auto-refresh interval in seconds"
    )
    
    # Filtering
    filtered_services = models.ManyToManyField(
        Service,
        blank=True,
        help_text="Services to include in this dashboard"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """Individual widgets within dashboards."""
    WIDGET_TYPES = [
        ('sla_summary', 'SLA Summary'),
        ('availability_chart', 'Availability Chart'),
        ('response_time_chart', 'Response Time Chart'),
        ('incident_list', 'Recent Incidents'),
        ('alert_summary', 'Alert Summary'),
        ('service_health', 'Service Health'),
        ('uptime_calendar', 'Uptime Calendar'),
        ('performance_metrics', 'Performance Metrics'),
        ('custom_metric', 'Custom Metric'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Small (1x1)'),
        ('medium', 'Medium (2x1)'),
        ('large', 'Large (2x2)'),
        ('wide', 'Wide (3x1)'),
        ('tall', 'Tall (1x3)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='widgets')
    
    # Widget configuration
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    title = models.CharField(max_length=200)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, default='medium')
    
    # Position in dashboard
    position_x = models.PositiveIntegerField(default=0)
    position_y = models.PositiveIntegerField(default=0)
    
    # Widget settings
    configuration = models.JSONField(
        default=dict,
        help_text="Widget-specific configuration (time range, services, etc.)"
    )
    
    # Filtering
    services = models.ManyToManyField(Service, blank=True)
    
    # Status
    is_visible = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position_y', 'position_x']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"


class UserPreferences(models.Model):
    """User-specific preferences for the dashboard."""
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]
    
    TIMEZONE_CHOICES = [
        ('UTC', 'UTC'),
        ('US/Eastern', 'US/Eastern'),
        ('US/Central', 'US/Central'),
        ('US/Mountain', 'US/Mountain'),
        ('US/Pacific', 'US/Pacific'),
        ('Europe/London', 'Europe/London'),
        ('Europe/Paris', 'Europe/Paris'),
        ('Asia/Tokyo', 'Asia/Tokyo'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_preferences')
    
    # Display preferences
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    default_dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    slack_notifications = models.BooleanField(default=False)
    notification_frequency = models.PositiveIntegerField(
        default=15,
        help_text="Notification frequency in minutes"
    )
    
    # Data preferences
    default_time_range = models.CharField(
        max_length=10,
        default='24h',
        help_text="Default time range for charts (1h, 24h, 7d, 30d)"
    )
    auto_refresh_enabled = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} preferences"


class SavedFilter(models.Model):
    """Saved filter configurations for quick access."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Filter configuration
    filter_config = models.JSONField(
        help_text="Filter configuration (services, time range, metrics, etc.)"
    )
    
    # Access control
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_filters')
    is_public = models.BooleanField(default=False)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-last_used', 'name']
    
    def __str__(self):
        return self.name


class DashboardView(models.Model):
    """Track dashboard view analytics."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(Dashboard, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dashboard_views')
    
    # View details
    viewed_at = models.DateTimeField()
    duration_seconds = models.PositiveIntegerField(default=0)
    
    # Context
    user_agent = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.user.username} viewed {self.dashboard.name}"


class ReportTemplate(models.Model):
    """Templates for automated SLA reports."""
    REPORT_FORMATS = [
        ('pdf', 'PDF'),
        ('html', 'HTML'),
        ('csv', 'CSV'),
        ('excel', 'Excel'),
    ]
    
    SCHEDULE_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('on_demand', 'On Demand'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Template configuration
    template_config = models.JSONField(
        help_text="Report template configuration (sections, metrics, styling)"
    )
    format = models.CharField(max_length=10, choices=REPORT_FORMATS, default='pdf')
    
    # Filtering
    services = models.ManyToManyField(Service, blank=True)
    
    # Scheduling
    schedule_type = models.CharField(max_length=15, choices=SCHEDULE_TYPES, default='on_demand')
    schedule_config = models.JSONField(
        default=dict,
        help_text="Schedule configuration (time, day of week, etc.)"
    )
    
    # Recipients
    email_recipients = models.TextField(
        blank=True,
        help_text="Comma-separated email addresses"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
