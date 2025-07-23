# Django SLA Dashboard

A comprehensive SLA (Service Level Agreement) monitoring and dashboard system built with Django and Django REST Framework.

## Features

### Core Functionality
- **Service Management**: Track multiple services with configurable SLA targets
- **Metric Collection**: Store and analyze availability, response time, throughput, and error rate metrics
- **Incident Tracking**: Monitor and manage SLA breaches and service incidents
- **Data Import**: CSV upload functionality with field mapping and validation
- **Alert System**: Configurable alert rules with notification channels
- **Dashboard**: Customizable dashboards with widgets and user preferences
- **Reports**: Automated SLA report generation

### Technical Features
- Django 5.2.4 with modern architecture
- REST API with Django REST Framework
- Multi-database routing support (PostgreSQL/MySQL)
- CSV processing with pandas
- Comprehensive admin interface
- UUID primary keys for security
- Filtering, search, and pagination
- User authentication and permissions

## Project Structure

```
django-sla/
├── sla_dashboard/          # Main Django project
├── sla_metrics/           # Core SLA metrics models and API
├── data_sources/          # Data import and CSV processing
├── alerts/               # Alert rules and notifications
├── dashboard/            # Dashboard widgets and user preferences
├── media/               # Uploaded files (CSV, etc.)
├── static/              # Static files
└── logs/                # Application logs
```

## Models Overview

### SLA Metrics App
- **ServiceType**: Categories for services (API, Web, Database, etc.)
- **Service**: Individual services with SLA targets
- **SLAMetric**: Time-series metric data (availability, response time, etc.)
- **SLAIncident**: Track SLA violations and incidents
- **SLAReport**: Generated periodic SLA reports

### Data Sources App
- **DataSource**: External data connections (CSV, API, Database)
- **DataSourceMapping**: Field mappings for data transformation
- **CSVUpload**: Track CSV file uploads and processing
- **DataImportLog**: Audit log for data imports
- **ExternalDataConnection**: Database connection management

### Alerts App
- **AlertRule**: Configurable alert conditions
- **Alert**: Individual alert instances
- **NotificationChannel**: Email, Slack, webhook notifications
- **AlertRuleNotification**: Link rules to notification channels
- **NotificationLog**: Track sent notifications
- **AlertEscalation**: Escalation rules for unacknowledged alerts

### Dashboard App
- **Dashboard**: Custom dashboard configurations
- **DashboardWidget**: Individual dashboard components
- **UserPreferences**: User-specific settings
- **SavedFilter**: Reusable filter configurations
- **ReportTemplate**: Automated report templates

## API Endpoints

### SLA Metrics API (`/api/v1/sla/`)
- `GET/POST /service-types/` - List/create service types
- `GET/PUT/DELETE /service-types/{id}/` - Service type details
- `GET/POST /services/` - List/create services
- `GET/PUT/DELETE /services/{id}/` - Service details
- `GET/POST /metrics/` - List/create SLA metrics
- `GET/PUT/DELETE /metrics/{id}/` - Metric details
- `GET/POST /incidents/` - List/create incidents
- `GET/PUT/DELETE /incidents/{id}/` - Incident details
- `GET/POST /reports/` - List/create reports
- `GET/PUT/DELETE /reports/{id}/` - Report details
- `GET /dashboard/stats/` - Dashboard statistics
- `GET /services/{id}/metrics/chart/` - Chart data
- `GET /services/{id}/availability/` - Availability summary

### Data Sources API (`/api/v1/data-sources/`)
- `POST /csv/upload/` - Upload CSV file
- `GET /csv/status/{id}/` - Upload status
- `POST /csv/process/{id}/` - Process uploaded CSV
- `GET /csv/history/` - Upload history
- `GET/POST /sources/` - List/create data sources
- `GET/PUT/DELETE /sources/{id}/` - Data source details
- `GET/POST /mappings/` - List/create field mappings
- `GET/PUT/DELETE /mappings/{id}/` - Mapping details
- `GET /import-logs/` - Import audit logs

## Installation & Setup

### 1. Environment Setup
```bash
# Clone the repository
cd django-sla

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration
```bash
# For SQLite (development)
python manage.py migrate

# For PostgreSQL (production)
# Update settings.py database configuration
# Create database and run migrations
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

Access the application:
- Admin Interface: http://localhost:8000/admin/
- API Documentation: http://localhost:8000/api/v1/

## CSV Upload Format

The system supports CSV uploads with the following fields:

### Required Fields
- `service_name` or `service` - Name of the service
- Metric fields (at least one):
  - `availability` - Availability percentage
  - `response_time` - Response time in milliseconds
  - `throughput` - Requests per second
  - `error_rate` - Error percentage

### Optional Fields
- `timestamp` - When the metric was recorded
- `uptime_seconds` - Total uptime in seconds
- `downtime_seconds` - Total downtime in seconds
- `total_requests` - Total number of requests
- `failed_requests` - Number of failed requests
- `unit` - Unit of measurement
- `notes` - Additional notes

### Example CSV
```csv
service_name,timestamp,availability,response_time,uptime_seconds,total_requests,failed_requests
Web API,2024-01-01 12:00:00,99.9,150,3590,1000,1
Database,2024-01-01 12:00:00,99.8,50,3588,500,1
```

## Configuration

### Environment Variables (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=sla_dashboard
DB_USER=sla_user
DB_PASSWORD=sla_password
DB_HOST=localhost
DB_PORT=5432
```

### Key Settings
- `DATABASES`: Database configuration with routing support
- `REST_FRAMEWORK`: API pagination and authentication
- `CORS_ALLOWED_ORIGINS`: Frontend CORS configuration
- `MEDIA_ROOT`: File upload directory
- `LOGGING`: Application logging configuration

## Development

### Adding New Metrics
1. Create data source in admin interface
2. Configure field mappings for CSV columns
3. Upload CSV file via API or admin
4. Process uploaded data

### Extending Models
- All models use UUID primary keys for security
- Models include created/updated timestamps
- Relationships use proper related_name attributes
- Indexes are configured for performance

### API Development
- Uses Django REST Framework with ViewSets
- Includes filtering, search, and ordering
- Comprehensive serializers for all models
- Proper error handling and validation

## Next Steps

### For Production Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Set up Redis for caching
4. Configure Celery for background tasks
5. Set up monitoring and logging
6. Configure email/Slack notifications
7. Set up automated backups

### Frontend Development
1. Create React/Vue.js frontend
2. Implement dashboard visualizations
3. Add real-time updates with WebSockets
4. Create mobile-responsive interface

### Additional Features
1. Real-time metric collection
2. Advanced alerting with ML
3. Multi-tenant support
4. API rate limiting
5. Advanced reporting with charts
6. Integration with monitoring tools

## License

This project is built for educational and development purposes.

## Architecture Decisions

### Database Design
- UUID primary keys for security and distribution
- Proper foreign key relationships with cascade options
- Indexes on frequently queried fields
- Database routing for multi-source support

### API Design
- RESTful endpoints following Django conventions
- Comprehensive filtering and search capabilities
- Proper HTTP status codes and error handling
- Pagination for large datasets

### Security Considerations
- Environment-based configuration
- Password fields marked as write-only
- Proper user authentication integration
- CORS configuration for frontend access

### Performance Optimizations
- Database query optimization with select_related
- Proper indexing on models
- Pagination to handle large datasets
- File upload size limits and validation