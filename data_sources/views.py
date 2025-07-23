"""
Django REST Framework views for Data Sources.
"""

from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import DataSource, DataSourceMapping, CSVUpload, DataImportLog
from .serializers import (
    DataSourceSerializer, DataSourceMappingSerializer, 
    CSVUploadSerializer, DataImportLogSerializer
)
from .csv_processor import CSVProcessor


class DataSourceListCreateView(generics.ListCreateAPIView):
    """List all data sources or create a new data source."""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source_type', 'status', 'is_enabled']
    search_fields = ['name', 'description']


class DataSourceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a data source."""
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer


class DataSourceMappingListCreateView(generics.ListCreateAPIView):
    """List all data source mappings or create new mappings."""
    queryset = DataSourceMapping.objects.select_related('data_source')
    serializer_class = DataSourceMappingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['data_source', 'target_metric_type', 'is_active']
    search_fields = ['source_field', 'source_table']


class DataSourceMappingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a data source mapping."""
    queryset = DataSourceMapping.objects.select_related('data_source')
    serializer_class = DataSourceMappingSerializer


class CSVUploadView(APIView):
    """Handle CSV file uploads."""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        """Upload a CSV file for processing."""
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded_file = request.FILES['file']
        
        # Validate file type
        if not uploaded_file.name.lower().endswith('.csv'):
            return Response(
                {'error': 'Only CSV files are allowed'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 50MB)
        if uploaded_file.size > 50 * 1024 * 1024:
            return Response(
                {'error': 'File size too large. Maximum 50MB allowed.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional data source
        data_source_id = request.data.get('data_source_id')
        data_source = None
        if data_source_id:
            try:
                data_source = DataSource.objects.get(id=data_source_id)
            except DataSource.DoesNotExist:
                return Response(
                    {'error': 'Invalid data source ID'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create CSV upload record
        csv_upload = CSVUpload.objects.create(
            file_name=uploaded_file.name,
            file_path=uploaded_file,
            file_size=uploaded_file.size,
            data_source=data_source,
            uploaded_by=request.user if request.user.is_authenticated else None
        )
        
        serializer = CSVUploadSerializer(csv_upload)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CSVUploadStatusView(APIView):
    """Get the status of a CSV upload."""
    
    def get(self, request, upload_id):
        """Get upload status and processing progress."""
        csv_upload = get_object_or_404(CSVUpload, id=upload_id)
        serializer = CSVUploadSerializer(csv_upload)
        return Response(serializer.data)


class ProcessCSVView(APIView):
    """Process an uploaded CSV file."""
    
    def post(self, request, upload_id):
        """Start processing the uploaded CSV file."""
        csv_upload = get_object_or_404(CSVUpload, id=upload_id)
        
        # Check if already processed or processing
        if csv_upload.status in ['processing', 'completed']:
            return Response(
                {'error': f'File is already {csv_upload.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if file exists
        if not csv_upload.file_path or not csv_upload.file_path.path:
            return Response(
                {'error': 'File not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Process the CSV file
            processor = CSVProcessor(
                csv_upload, 
                user=request.user if request.user.is_authenticated else None
            )
            
            success = processor.process()
            
            # Return updated status
            csv_upload.refresh_from_db()
            serializer = CSVUploadSerializer(csv_upload)
            
            if success:
                return Response({
                    'message': 'CSV processing completed',
                    'upload': serializer.data
                })
            else:
                return Response({
                    'message': 'CSV processing failed',
                    'upload': serializer.data
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {'error': f'Processing failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CSVUploadListView(generics.ListAPIView):
    """List CSV upload history."""
    queryset = CSVUpload.objects.all()
    serializer_class = CSVUploadSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'data_source']
    search_fields = ['file_name']
    ordering_fields = ['uploaded_at', 'file_size']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by user if authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.filter(uploaded_by=self.request.user)
        return queryset


class DataImportLogListView(generics.ListAPIView):
    """List data import logs."""
    queryset = DataImportLog.objects.select_related('data_source', 'csv_upload', 'triggered_by')
    serializer_class = DataImportLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['import_type', 'result', 'data_source']
    search_fields = ['data_source__name']
    ordering_fields = ['started_at', 'processing_time_seconds']
    ordering = ['-started_at']
