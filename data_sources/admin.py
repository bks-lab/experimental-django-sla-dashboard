"""
Django admin configuration for Data Sources models.
"""

from django.contrib import admin
from .models import DataSource, DataSourceMapping, CSVUpload, DataImportLog, ExternalDataConnection


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'status', 'is_enabled', 'last_sync', 'created_by']
    list_filter = ['source_type', 'status', 'is_enabled', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'source_type')
        }),
        ('Connection Details', {
            'fields': ('connection_string', 'api_key', 'username', 'password'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('polling_interval', 'is_enabled', 'status')
        }),
        ('Metadata', {
            'fields': ('created_by', 'last_sync'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DataSourceMapping)
class DataSourceMappingAdmin(admin.ModelAdmin):
    list_display = ['data_source', 'source_field', 'target_metric_type', 'is_active']
    list_filter = ['target_metric_type', 'is_active', 'data_source__source_type']
    search_fields = ['source_field', 'source_table', 'data_source__name']
    ordering = ['data_source__name', 'source_field']


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'status', 'total_rows', 'processed_rows', 'failed_rows', 'processing_progress', 'uploaded_at']
    list_filter = ['status', 'uploaded_at', 'data_source']
    search_fields = ['file_name']
    ordering = ['-uploaded_at']
    readonly_fields = ['file_size', 'processing_progress']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'file_path', 'file_size', 'data_source')
        }),
        ('Processing Status', {
            'fields': ('status', 'total_rows', 'processed_rows', 'failed_rows', 'processing_progress')
        }),
        ('Processing Times', {
            'fields': ('processing_started_at', 'processing_completed_at'),
            'classes': ('collapse',)
        }),
        ('Errors', {
            'fields': ('error_log',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('uploaded_by',),
            'classes': ('collapse',)
        }),
    )
    
    def processing_progress(self, obj):
        return f"{obj.processing_progress:.1f}%"
    processing_progress.short_description = 'Progress'


@admin.register(DataImportLog)
class DataImportLogAdmin(admin.ModelAdmin):
    list_display = ['data_source', 'import_type', 'result', 'records_processed', 'records_created', 'processing_time_seconds', 'started_at']
    list_filter = ['import_type', 'result', 'started_at', 'data_source']
    search_fields = ['data_source__name']
    ordering = ['-started_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Import Information', {
            'fields': ('data_source', 'import_type', 'result', 'csv_upload')
        }),
        ('Processing Results', {
            'fields': ('records_processed', 'records_created', 'records_updated', 'records_failed')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'processing_time_seconds')
        }),
        ('Error Details', {
            'fields': ('error_details',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('triggered_by',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExternalDataConnection)
class ExternalDataConnectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'connection_type', 'host', 'port', 'status', 'last_test']
    list_filter = ['connection_type', 'status', 'ssl_required']
    search_fields = ['name', 'host', 'database_name']
    ordering = ['name']
    
    fieldsets = (
        ('Connection Information', {
            'fields': ('name', 'connection_type', 'data_source')
        }),
        ('Connection Parameters', {
            'fields': ('host', 'port', 'database_name', 'username', 'password')
        }),
        ('Options', {
            'fields': ('ssl_required', 'connection_timeout')
        }),
        ('Status', {
            'fields': ('status', 'last_test', 'last_error'),
            'classes': ('collapse',)
        }),
    )
