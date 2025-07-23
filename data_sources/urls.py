"""
URL configuration for Data Sources API.
"""

from django.urls import path
from . import views

app_name = 'data_sources'

urlpatterns = [
    # CSV Upload
    path('csv/upload/', views.CSVUploadView.as_view(), name='csv-upload'),
    path('csv/status/<uuid:upload_id>/', views.CSVUploadStatusView.as_view(), name='csv-upload-status'),
    path('csv/process/<uuid:upload_id>/', views.ProcessCSVView.as_view(), name='csv-process'),
    path('csv/history/', views.CSVUploadListView.as_view(), name='csv-upload-history'),
    
    # Data Sources
    path('sources/', views.DataSourceListCreateView.as_view(), name='datasource-list'),
    path('sources/<uuid:pk>/', views.DataSourceRetrieveUpdateDestroyView.as_view(), name='datasource-detail'),
    
    # Data Source Mappings
    path('mappings/', views.DataSourceMappingListCreateView.as_view(), name='mapping-list'),
    path('mappings/<int:pk>/', views.DataSourceMappingRetrieveUpdateDestroyView.as_view(), name='mapping-detail'),
    
    # Import Logs
    path('import-logs/', views.DataImportLogListView.as_view(), name='import-logs'),
]