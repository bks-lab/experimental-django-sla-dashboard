"""
Data Sources models for managing external data connections and CSV uploads.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator
import uuid


class DataSource(models.Model):
    """External data sources for SLA metrics."""
    SOURCE_TYPES = [
        ('database', 'Database'),
        ('api', 'REST API'),
        ('csv', 'CSV Upload'),
        ('webhook', 'Webhook'),
        ('file', 'File Upload'),
        ('monitoring', 'Monitoring Tool'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('testing', 'Testing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=15, choices=SOURCE_TYPES)
    
    # Connection details
    connection_string = models.TextField(blank=True, help_text="Database connection or API endpoint")
    api_key = models.CharField(max_length=500, blank=True)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=200, blank=True)  # Should be encrypted in production
    
    # Configuration
    polling_interval = models.PositiveIntegerField(
        default=300, 
        help_text="Polling interval in seconds"
    )
    is_enabled = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"


class DataSourceMapping(models.Model):
    """Field mappings for data source to SLA metric conversion."""
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='mappings')
    
    # Source field information
    source_field = models.CharField(max_length=200, help_text="Field name in source data")
    source_table = models.CharField(max_length=200, blank=True, help_text="Table name if applicable")
    
    # Target mapping
    target_metric_type = models.CharField(
        max_length=20,
        choices=[
            ('availability', 'Availability'),
            ('response_time', 'Response Time'),
            ('throughput', 'Throughput'),
            ('error_rate', 'Error Rate'),
            ('custom', 'Custom Metric'),
        ]
    )
    target_service_field = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Field to identify service (if not specified in upload)"
    )
    
    # Data transformation
    transformation_rule = models.TextField(
        blank=True,
        help_text="JSON configuration for data transformation"
    )
    unit_conversion = models.CharField(max_length=100, blank=True)
    
    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['data_source', 'source_field']
    
    def __str__(self):
        return f"{self.data_source.name}: {self.source_field} -> {self.target_metric_type}"


class CSVUpload(models.Model):
    """Track CSV file uploads and processing."""
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='csv_uploads/')
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    
    # Processing information
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='uploaded')
    total_rows = models.PositiveIntegerField(default=0)
    processed_rows = models.PositiveIntegerField(default=0)
    failed_rows = models.PositiveIntegerField(default=0)
    
    # Data source association
    data_source = models.ForeignKey(
        DataSource, 
        on_delete=models.CASCADE, 
        related_name='csv_uploads',
        null=True,
        blank=True
    )
    
    # Processing results
    error_log = models.TextField(blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.status}"
    
    @property
    def processing_progress(self):
        """Calculate processing progress percentage."""
        if self.total_rows == 0:
            return 0
        return (self.processed_rows / self.total_rows) * 100


class DataImportLog(models.Model):
    """Log data import activities and results."""
    IMPORT_TYPES = [
        ('csv', 'CSV Upload'),
        ('api', 'API Sync'),
        ('database', 'Database Query'),
        ('manual', 'Manual Entry'),
    ]
    
    RESULT_TYPES = [
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, related_name='import_logs')
    import_type = models.CharField(max_length=10, choices=IMPORT_TYPES)
    
    # Import results
    result = models.CharField(max_length=10, choices=RESULT_TYPES)
    records_processed = models.PositiveIntegerField(default=0)
    records_created = models.PositiveIntegerField(default=0)
    records_updated = models.PositiveIntegerField(default=0)
    records_failed = models.PositiveIntegerField(default=0)
    
    # Additional information
    error_details = models.TextField(blank=True)
    processing_time_seconds = models.PositiveIntegerField(default=0)
    
    # File reference for CSV uploads
    csv_upload = models.ForeignKey(
        CSVUpload,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='import_logs'
    )
    
    # Metadata
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()
    triggered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.data_source.name} - {self.import_type} - {self.result}"


class ExternalDataConnection(models.Model):
    """Test and manage external database connections."""
    CONNECTION_TYPES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('mssql', 'Microsoft SQL Server'),
        ('oracle', 'Oracle'),
        ('sqlite', 'SQLite'),
    ]
    
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('error', 'Connection Error'),
        ('testing', 'Testing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    connection_type = models.CharField(max_length=15, choices=CONNECTION_TYPES)
    
    # Connection parameters
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    database_name = models.CharField(max_length=200)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=200)  # Should be encrypted
    
    # Connection options
    ssl_required = models.BooleanField(default=False)
    connection_timeout = models.PositiveIntegerField(default=30)
    
    # Status and testing
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='disconnected')
    last_test = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    
    # Associated data source
    data_source = models.OneToOneField(
        DataSource,
        on_delete=models.CASCADE,
        related_name='external_connection'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"
