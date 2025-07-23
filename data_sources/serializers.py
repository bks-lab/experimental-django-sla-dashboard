"""
Django REST Framework serializers for Data Sources models.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import DataSource, DataSourceMapping, CSVUpload, DataImportLog, ExternalDataConnection


class DataSourceSerializer(serializers.ModelSerializer):
    """Serializer for DataSource model."""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = DataSource
        fields = [
            'id', 'name', 'description', 'source_type', 'connection_string',
            'api_key', 'username', 'password', 'polling_interval', 'is_enabled',
            'last_sync', 'status', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_sync']
        extra_kwargs = {
            'password': {'write_only': True},
            'api_key': {'write_only': True}
        }


class DataSourceMappingSerializer(serializers.ModelSerializer):
    """Serializer for DataSourceMapping model."""
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    
    class Meta:
        model = DataSourceMapping
        fields = [
            'id', 'data_source', 'data_source_name', 'source_field', 'source_table',
            'target_metric_type', 'target_service_field', 'transformation_rule',
            'unit_conversion', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CSVUploadSerializer(serializers.ModelSerializer):
    """Serializer for CSVUpload model."""
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    processing_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = CSVUpload
        fields = [
            'id', 'file_name', 'file_path', 'file_size', 'status', 'total_rows',
            'processed_rows', 'failed_rows', 'processing_progress', 'data_source',
            'data_source_name', 'error_log', 'processing_started_at',
            'processing_completed_at', 'uploaded_by', 'uploaded_by_username',
            'uploaded_at'
        ]
        read_only_fields = [
            'id', 'file_size', 'status', 'total_rows', 'processed_rows',
            'failed_rows', 'error_log', 'processing_started_at',
            'processing_completed_at', 'uploaded_at'
        ]


class DataImportLogSerializer(serializers.ModelSerializer):
    """Serializer for DataImportLog model."""
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    triggered_by_username = serializers.CharField(source='triggered_by.username', read_only=True)
    csv_upload_filename = serializers.CharField(source='csv_upload.file_name', read_only=True)
    
    class Meta:
        model = DataImportLog
        fields = [
            'id', 'data_source', 'data_source_name', 'import_type', 'result',
            'records_processed', 'records_created', 'records_updated', 'records_failed',
            'error_details', 'processing_time_seconds', 'csv_upload', 'csv_upload_filename',
            'started_at', 'completed_at', 'triggered_by', 'triggered_by_username'
        ]
        read_only_fields = ['id']


class ExternalDataConnectionSerializer(serializers.ModelSerializer):
    """Serializer for ExternalDataConnection model."""
    data_source_name = serializers.CharField(source='data_source.name', read_only=True)
    
    class Meta:
        model = ExternalDataConnection
        fields = [
            'id', 'name', 'connection_type', 'host', 'port', 'database_name',
            'username', 'password', 'ssl_required', 'connection_timeout',
            'status', 'last_test', 'last_error', 'data_source', 'data_source_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'last_test', 'last_error', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }