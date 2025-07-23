"""
Alerts models for SLA monitoring and notification management.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from sla_metrics.models import Service, SLAMetric
import uuid


class AlertRule(models.Model):
    """Rules for triggering SLA alerts."""
    CONDITION_TYPES = [
        ('threshold', 'Threshold'),
        ('trend', 'Trend'),
        ('anomaly', 'Anomaly Detection'),
        ('duration', 'Duration Based'),
    ]
    
    OPERATOR_CHOICES = [
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('eq', 'Equal'),
        ('ne', 'Not Equal'),
    ]
    
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('emergency', 'Emergency'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Rule configuration
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='alert_rules')
    metric_type = models.CharField(
        max_length=20,
        choices=[
            ('availability', 'Availability'),
            ('response_time', 'Response Time'),
            ('throughput', 'Throughput'),
            ('error_rate', 'Error Rate'),
            ('custom', 'Custom Metric'),
        ]
    )
    
    # Condition settings
    condition_type = models.CharField(max_length=15, choices=CONDITION_TYPES, default='threshold')
    operator = models.CharField(max_length=5, choices=OPERATOR_CHOICES, default='lt')
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4)
    duration_minutes = models.PositiveIntegerField(
        default=5,
        help_text="Duration condition must be met before triggering"
    )
    
    # Alert settings
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='warning')
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['service__name', 'name']
    
    def __str__(self):
        return f"{self.service.name} - {self.name}"


class Alert(models.Model):
    """Individual alert instances triggered by alert rules."""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('suppressed', 'Suppressed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='alerts')
    
    # Alert details
    title = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    severity = models.CharField(max_length=10, choices=AlertRule.SEVERITY_CHOICES)
    
    # Trigger information
    triggered_at = models.DateTimeField()
    triggered_value = models.DecimalField(max_digits=15, decimal_places=4)
    metric_snapshot = models.ForeignKey(
        SLAMetric,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='triggered_alerts'
    )
    
    # Resolution information
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    
    # Additional context
    resolution_notes = models.TextField(blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_rule.service.name} - {self.title}"
    
    @property
    def is_active(self):
        """Check if alert is still active."""
        return self.status in ['open', 'acknowledged']
    
    @property
    def duration(self):
        """Calculate alert duration."""
        from django.utils import timezone
        end_time = self.resolved_at or timezone.now()
        return end_time - self.triggered_at


class NotificationChannel(models.Model):
    """Notification channels for alert delivery."""
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS'),
        ('teams', 'Microsoft Teams'),
        ('pagerduty', 'PagerDuty'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    channel_type = models.CharField(max_length=15, choices=CHANNEL_TYPES)
    
    # Configuration
    configuration = models.JSONField(
        help_text="Channel-specific configuration (webhook URL, email addresses, etc.)"
    )
    is_enabled = models.BooleanField(default=True)
    
    # Rate limiting
    rate_limit_minutes = models.PositiveIntegerField(
        default=5,
        help_text="Minimum minutes between notifications"
    )
    last_notification = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.channel_type})"


class AlertRuleNotification(models.Model):
    """Associate alert rules with notification channels."""
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE)
    notification_channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    
    # Notification settings
    notify_on_trigger = models.BooleanField(default=True)
    notify_on_acknowledge = models.BooleanField(default=False)
    notify_on_resolve = models.BooleanField(default=True)
    
    # Escalation
    escalation_delay_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Minutes to wait before escalating unacknowledged alerts"
    )
    
    class Meta:
        unique_together = ['alert_rule', 'notification_channel']
    
    def __str__(self):
        return f"{self.alert_rule.name} -> {self.notification_channel.name}"


class NotificationLog(models.Model):
    """Log of sent notifications."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='notifications')
    notification_channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    
    # Notification details
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    message_content = models.TextField()
    retry_count = models.PositiveIntegerField(default=0)
    
    # Timing
    scheduled_at = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    response_code = models.CharField(max_length=10, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert.title} -> {self.notification_channel.name} ({self.status})"


class AlertEscalation(models.Model):
    """Escalation rules for unacknowledged alerts."""
    ESCALATION_TYPES = [
        ('time', 'Time Based'),
        ('severity', 'Severity Based'),
        ('manual', 'Manual'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    alert_rule = models.ForeignKey(AlertRule, on_delete=models.CASCADE, related_name='escalations')
    
    # Escalation settings
    escalation_type = models.CharField(max_length=10, choices=ESCALATION_TYPES, default='time')
    delay_minutes = models.PositiveIntegerField(help_text="Minutes before escalating")
    target_users = models.ManyToManyField(User, blank=True)
    target_channels = models.ManyToManyField(NotificationChannel, blank=True)
    
    # Conditions
    is_active = models.BooleanField(default=True)
    max_escalations = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of escalations per alert"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['delay_minutes']
    
    def __str__(self):
        return f"{self.alert_rule.name} - {self.name}"
