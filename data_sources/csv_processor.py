"""
CSV processing functionality for data import.
"""

import pandas as pd
import csv
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.models import User
from typing import Dict, List, Any, Optional

from .models import CSVUpload, DataImportLog, DataSource, DataSourceMapping
from sla_metrics.models import Service, SLAMetric


class CSVProcessor:
    """Process CSV uploads and convert to SLA metrics."""
    
    def __init__(self, csv_upload: CSVUpload, user: Optional[User] = None):
        self.csv_upload = csv_upload
        self.user = user
        self.errors = []
        self.processed_rows = 0
        self.created_records = 0
        self.failed_rows = 0
    
    def process(self) -> bool:
        """Process the CSV file and create SLA metrics."""
        try:
            # Update status to processing
            self.csv_upload.status = 'processing'
            self.csv_upload.processing_started_at = timezone.now()
            self.csv_upload.save()
            
            # Read and validate CSV file
            df = self._read_csv_file()
            if df is None:
                return False
            
            # Get data source mappings
            mappings = self._get_data_source_mappings()
            if not mappings:
                self.errors.append("No data source mappings found")
                return False
            
            # Process each row
            self.csv_upload.total_rows = len(df)
            self.csv_upload.save()
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        self._process_row(row, mappings)
                        self.processed_rows += 1
                    except Exception as e:
                        self.failed_rows += 1
                        self.errors.append(f"Row {index + 1}: {str(e)}")
            
            # Update final status
            self._finalize_processing()
            return True
            
        except Exception as e:
            self._handle_processing_error(str(e))
            return False
    
    def _read_csv_file(self) -> Optional[pd.DataFrame]:
        """Read and validate the CSV file."""
        try:
            # Try to read with pandas for better error handling
            df = pd.read_csv(self.csv_upload.file_path.path)
            
            if df.empty:
                self.errors.append("CSV file is empty")
                return None
            
            return df
            
        except FileNotFoundError:
            self.errors.append("CSV file not found")
            return None
        except pd.errors.EmptyDataError:
            self.errors.append("CSV file is empty")
            return None
        except Exception as e:
            self.errors.append(f"Error reading CSV file: {str(e)}")
            return None
    
    def _get_data_source_mappings(self) -> List[DataSourceMapping]:
        """Get active data source mappings."""
        if self.csv_upload.data_source:
            return list(self.csv_upload.data_source.mappings.filter(is_active=True))
        else:
            # Try to find a default CSV data source
            try:
                csv_data_source = DataSource.objects.filter(
                    source_type='csv',
                    is_enabled=True
                ).first()
                
                if csv_data_source:
                    return list(csv_data_source.mappings.filter(is_active=True))
            except DataSource.DoesNotExist:
                pass
        
        return []
    
    def _process_row(self, row: pd.Series, mappings: List[DataSourceMapping]) -> None:
        """Process a single CSV row."""
        created_metrics = []
        
        for mapping in mappings:
            try:
                # Extract value from CSV row
                if mapping.source_field not in row:
                    continue
                
                value = row[mapping.source_field]
                if pd.isna(value):
                    continue
                
                # Find or create service
                service = self._get_or_create_service(row, mapping)
                if not service:
                    continue
                
                # Create SLA metric
                metric = self._create_sla_metric(row, mapping, service, value)
                if metric:
                    created_metrics.append(metric)
                    self.created_records += 1
            
            except Exception as e:
                raise Exception(f"Error processing mapping {mapping.source_field}: {str(e)}")
    
    def _get_or_create_service(self, row: pd.Series, mapping: DataSourceMapping) -> Optional[Service]:
        """Get or create a service based on the mapping."""
        service_name = None
        
        # Try to get service name from the specified field
        if mapping.target_service_field and mapping.target_service_field in row:
            service_name = str(row[mapping.target_service_field]).strip()
        elif 'service_name' in row:
            service_name = str(row['service_name']).strip()
        elif 'service' in row:
            service_name = str(row['service']).strip()
        
        if not service_name:
            raise Exception("Service name not found in CSV row")
        
        # Try to find existing service
        try:
            return Service.objects.get(name=service_name)
        except Service.DoesNotExist:
            # Create new service with default values
            from sla_metrics.models import ServiceType
            
            default_service_type, _ = ServiceType.objects.get_or_create(
                name='Imported',
                defaults={'description': 'Services imported from CSV'}
            )
            
            return Service.objects.create(
                name=service_name,
                service_type=default_service_type,
                availability_target=99.9,
                response_time_target=1000,
                description=f'Imported from CSV upload: {self.csv_upload.file_name}'
            )
    
    def _create_sla_metric(self, row: pd.Series, mapping: DataSourceMapping, 
                          service: Service, value: Any) -> Optional[SLAMetric]:
        """Create an SLA metric from CSV data."""
        try:
            # Parse timestamp
            timestamp = self._parse_timestamp(row)
            if not timestamp:
                timestamp = timezone.now()
            
            # Parse and convert value
            numeric_value = self._parse_numeric_value(value, mapping)
            if numeric_value is None:
                return None
            
            # Extract additional fields
            uptime_seconds = self._get_optional_field(row, 'uptime_seconds', 0)
            downtime_seconds = self._get_optional_field(row, 'downtime_seconds', 0)
            total_requests = self._get_optional_field(row, 'total_requests', 0)
            failed_requests = self._get_optional_field(row, 'failed_requests', 0)
            
            # Create SLA metric
            return SLAMetric.objects.create(
                service=service,
                metric_type=mapping.target_metric_type,
                timestamp=timestamp,
                value=numeric_value,
                unit=self._get_optional_field(row, 'unit', ''),
                uptime_seconds=uptime_seconds,
                downtime_seconds=downtime_seconds,
                total_requests=total_requests,
                failed_requests=failed_requests,
                source=f'CSV Upload: {self.csv_upload.file_name}',
                notes=self._get_optional_field(row, 'notes', '')
            )
            
        except Exception as e:
            raise Exception(f"Error creating SLA metric: {str(e)}")
    
    def _parse_timestamp(self, row: pd.Series) -> Optional[timezone.datetime]:
        """Parse timestamp from CSV row."""
        timestamp_fields = ['timestamp', 'time', 'date', 'created_at']
        
        for field in timestamp_fields:
            if field in row and not pd.isna(row[field]):
                try:
                    return pd.to_datetime(row[field])
                except Exception:
                    continue
        
        return None
    
    def _parse_numeric_value(self, value: Any, mapping: DataSourceMapping) -> Optional[float]:
        """Parse and convert numeric value."""
        try:
            # Remove any percentage signs or units
            if isinstance(value, str):
                value = value.replace('%', '').replace(',', '').strip()
            
            numeric_value = float(value)
            
            # Apply unit conversion if specified
            if mapping.unit_conversion:
                # Simple unit conversions
                conversions = {
                    'ms_to_seconds': lambda x: x / 1000,
                    'percentage_to_decimal': lambda x: x / 100,
                    'bytes_to_mb': lambda x: x / (1024 * 1024)
                }
                
                if mapping.unit_conversion in conversions:
                    numeric_value = conversions[mapping.unit_conversion](numeric_value)
            
            return numeric_value
            
        except (ValueError, TypeError):
            return None
    
    def _get_optional_field(self, row: pd.Series, field_name: str, default: Any = None) -> Any:
        """Get optional field from row with default value."""
        if field_name in row and not pd.isna(row[field_name]):
            try:
                if isinstance(default, int):
                    return int(float(row[field_name]))
                elif isinstance(default, float):
                    return float(row[field_name])
                else:
                    return str(row[field_name])
            except (ValueError, TypeError):
                pass
        
        return default
    
    def _finalize_processing(self) -> None:
        """Finalize the processing and update status."""
        self.csv_upload.processed_rows = self.processed_rows
        self.csv_upload.failed_rows = self.failed_rows
        self.csv_upload.processing_completed_at = timezone.now()
        
        if self.failed_rows == 0:
            self.csv_upload.status = 'completed'
        elif self.processed_rows > 0:
            self.csv_upload.status = 'completed'  # Partial success
        else:
            self.csv_upload.status = 'failed'
        
        # Store errors
        if self.errors:
            self.csv_upload.error_log = '\n'.join(self.errors[:100])  # Limit errors
        
        self.csv_upload.save()
        
        # Create import log
        self._create_import_log()
    
    def _create_import_log(self) -> None:
        """Create an import log entry."""
        processing_time = 0
        if self.csv_upload.processing_started_at and self.csv_upload.processing_completed_at:
            delta = self.csv_upload.processing_completed_at - self.csv_upload.processing_started_at
            processing_time = int(delta.total_seconds())
        
        # Determine result
        if self.failed_rows == 0:
            result = 'success'
        elif self.processed_rows > 0:
            result = 'partial'
        else:
            result = 'failed'
        
        DataImportLog.objects.create(
            data_source=self.csv_upload.data_source,
            csv_upload=self.csv_upload,
            import_type='csv',
            result=result,
            records_processed=self.processed_rows + self.failed_rows,
            records_created=self.created_records,
            records_updated=0,
            records_failed=self.failed_rows,
            error_details='\n'.join(self.errors) if self.errors else '',
            processing_time_seconds=processing_time,
            started_at=self.csv_upload.processing_started_at or timezone.now(),
            completed_at=self.csv_upload.processing_completed_at or timezone.now(),
            triggered_by=self.user
        )
    
    def _handle_processing_error(self, error_message: str) -> None:
        """Handle processing errors."""
        self.csv_upload.status = 'failed'
        self.csv_upload.error_log = error_message
        self.csv_upload.processing_completed_at = timezone.now()
        self.csv_upload.save()
        
        # Create failure log
        DataImportLog.objects.create(
            data_source=self.csv_upload.data_source,
            csv_upload=self.csv_upload,
            import_type='csv',
            result='failed',
            records_processed=0,
            records_created=0,
            records_updated=0,
            records_failed=0,
            error_details=error_message,
            processing_time_seconds=0,
            started_at=self.csv_upload.processing_started_at or timezone.now(),
            completed_at=timezone.now(),
            triggered_by=self.user
        )