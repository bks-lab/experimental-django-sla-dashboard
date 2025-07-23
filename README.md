# Experimental Django SLA Dashboard

⚠️ **EXPERIMENTELLES PROJEKT** - Dies ist ein experimentelles Django SLA Dashboard System für Service Level Agreement Monitoring und Dashboarding.

## Über das Projekt

Ein umfassendes SLA (Service Level Agreement) Monitoring und Dashboard System, entwickelt mit Django und Django REST Framework. Das Projekt befindet sich in der experimentellen Phase und dient der Erforschung und Entwicklung von SLA-Monitoring-Lösungen.

## Features

### Kernfunktionalität

- **Service Management**: Verfolgung mehrerer Services mit konfigurierbaren SLA-Zielen
- **Metrik-Sammlung**: Speicherung und Analyse von Verfügbarkeit, Antwortzeit, Durchsatz und Fehlerrate
- **Incident Tracking**: Überwachung und Verwaltung von SLA-Verstößen und Service-Incidents
- **Datenimport**: CSV-Upload-Funktionalität mit Feldzuordnung und Validierung
- **Alert-System**: Konfigurierbare Alert-Regeln mit Benachrichtigungskanälen
- **Dashboard**: Anpassbare Dashboards mit Widgets und Benutzereinstellungen
- **Reports**: Automatisierte SLA-Report-Generierung

### Technische Features

- Django 5.2.4 mit moderner Architektur
- REST API mit Django REST Framework
- Multi-Database-Routing-Support (PostgreSQL/MySQL)
- CSV-Verarbeitung mit pandas
- Umfassende Admin-Oberfläche
- UUID-Primärschlüssel für Sicherheit
- Filterung, Suche und Paginierung
- Benutzerauthentifizierung und Berechtigungen

## Projektstruktur

```
django-sla/
├── sla_dashboard/          # Haupt-Django-Projekt
├── sla_metrics/           # Core SLA Metriken Modelle und API
├── data_sources/          # Datenimport und CSV-Verarbeitung
├── alerts/               # Alert-Regeln und Benachrichtigungen
├── dashboard/            # Dashboard-Widgets und Benutzereinstellungen
├── media/               # Hochgeladene Dateien (CSV, etc.)
├── static/              # Statische Dateien
└── logs/                # Anwendungslogs
```

## Experimenteller Status

### ⚠️ Wichtige Hinweise

- **Nicht für Produktion geeignet**: Dies ist ein experimentelles Projekt
- **Entwicklungsphase**: Das Projekt befindet sich in aktiver Entwicklung
- **Tests erforderlich**: Weitere Tests und Validierungen sind geplant
- **Performance-Optimierungen**: Weitere Optimierungen sind in Planung

### Bekannte Einschränkungen

- Grundlegende Funktionalität implementiert
- Weitere Tests erforderlich
- Performance-Optimierungen geplant
- Frontend-Integration in Entwicklung

## Installation & Setup

### Voraussetzungen

- Python 3.8+
- pip oder uv (empfohlen)

### 1. Repository klonen

```bash
git clone https://github.com/bks-lab/experimental-django-sla-dashboard.git
cd experimental-django-sla-dashboard
```

### 2. Virtuelle Umgebung erstellen

```bash
# Mit uv (empfohlen)
uv venv
source .venv/bin/activate

# Oder mit venv
python3 -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

```bash
# Mit uv
uv pip install -r requirements.txt

# Oder mit pip
pip install -r requirements.txt
```

### 4. Datenbank konfigurieren

```bash
# Für SQLite (Entwicklung)
python manage.py migrate

# Für PostgreSQL (Produktion)
# settings.py Datenbank-Konfiguration aktualisieren
# Datenbank erstellen und Migrationen ausführen
python manage.py migrate
```

### 5. Testdaten generieren

```bash
# Testdaten mit Admin-Benutzer erstellen
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sla_dashboard.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from sla_metrics.models import ServiceType, Service, SLAMetric, SLAIncident
from datetime import timedelta
import random
from decimal import Decimal

# Create admin user
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('👤 Created admin user (admin/admin123)')

# Create service types
types_data = [
    {'name': 'Web API', 'description': 'REST API services'},
    {'name': 'Database', 'description': 'Database services'},
    {'name': 'Web Application', 'description': 'Web applications'},
]

service_types = []
for data in types_data:
    service_type, created = ServiceType.objects.get_or_create(
        name=data['name'],
        defaults={'description': data['description']}
    )
    service_types.append(service_type)
    if created:
        print(f'📋 Created service type: {service_type.name}')

# Create services
service_names = [
    'User Authentication API', 'Payment Gateway', 'Email Service',
    'File Storage Service', 'Search Engine', 'Analytics API',
    'Notification Service', 'Order Management', 'Inventory System',
    'Customer Portal'
]

services = []
admin_user = User.objects.get(username='admin')

for name in service_names:
    service_type = random.choice(service_types)
    availability_target = Decimal(random.uniform(99.5, 99.9))
    response_time_target = random.randint(100, 500)

    service = Service.objects.create(
        name=name,
        service_type=service_type,
        description=f'Test service for {service_type.name}',
        owner=admin_user,
        availability_target=availability_target,
        response_time_target=response_time_target,
        is_active=True
    )
    services.append(service)
    print(f'🔧 Created service: {service.name}')

# Create metrics
now = timezone.now()
for service in services:
    print(f'📊 Generating metrics for {service.name}...')

    for day in range(7):
        date = now - timedelta(days=day)

        for hour in range(24):
            timestamp = date.replace(hour=hour, minute=0, second=0, microsecond=0)

            # Availability metric
            base_availability = float(service.availability_target)
            availability = max(95.0, min(100.0, base_availability + random.uniform(-0.5, 0.3)))

            SLAMetric.objects.create(
                service=service,
                metric_type='availability',
                timestamp=timestamp,
                value=Decimal(str(round(availability, 2))),
                unit='%',
                source='test_data'
            )

            # Response time metric
            base_response_time = service.response_time_target
            response_time = max(50, min(1000, base_response_time + random.uniform(-50, 150)))

            SLAMetric.objects.create(
                service=service,
                metric_type='response_time',
                timestamp=timestamp,
                value=Decimal(str(round(response_time, 1))),
                unit='ms',
                source='test_data'
            )

# Create incidents
for service in services[:5]:
    started_at = timezone.now() - timedelta(days=random.randint(1, 5))

    incident = SLAIncident.objects.create(
        service=service,
        title=f'Test incident for {service.name}',
        description=f'This is a test incident for {service.name}',
        severity=random.choice(['low', 'medium', 'high']),
        status='resolved',
        started_at=started_at,
        resolved_at=started_at + timedelta(hours=random.randint(1, 4)),
        affected_users=random.randint(100, 1000),
        revenue_impact=Decimal(str(random.uniform(100, 1000)))
    )
    print(f'🚨 Created incident: {incident.title}')

print('\\n✅ Test data generated successfully!')
print('\\n🔑 Admin credentials:')
print('   Username: admin')
print('   Password: admin123')
print('\\n🌐 Access your dashboard:')
print('   Admin: http://localhost:8000/admin/')
print('   Dashboard: http://localhost:8000/dashboard/')
print('   API: http://localhost:8000/api/v1/sla/')
"
```

### 6. Entwicklungsserver starten

```bash
python manage.py runserver
```

## Zugriff auf die Anwendung

- **📊 Dashboard**: http://localhost:8000/dashboard/

  - Moderne Visualisierung mit Charts und Metriken
  - Real-time Updates
  - Service-Status-Übersicht
  - **Funktioniert ohne Login!**

- **🔧 Admin-Interface**: http://localhost:8000/admin/

  - Login: `admin` / `admin123`
  - Vollständige Verwaltung aller Daten
  - Service-Management, Incidents, Reports

- **📡 API-Endpunkte**: http://localhost:8000/api/v1/sla/
  - REST API für alle SLA-Daten
  - JSON-Format für Frontend-Integration

## Dashboard Features

### 📊 Was du im Dashboard siehst:

- **Key Metrics**:

  - Gesamtverfügbarkeit: ~99.5%
  - Aktive Incidents: 5
  - Durchschnittliche Antwortzeit: ~200ms
  - Services überwacht: 10

- **Charts**:

  - Verfügbarkeits-Timeline (24h)
  - Antwortzeit-Verteilung
  - SLA-Compliance Donut-Chart

- **Service-Status-Tabelle**:

  - Alle Services mit aktuellen Metriken
  - Status-Indikatoren (grün/gelb/rot)
  - Verfügbarkeit und Antwortzeiten

- **Alerts & Incidents**:
  - Aktuelle Benachrichtigungen
  - Incident-Historie

## API Endpunkte

### SLA Metrics API (`/api/v1/sla/`)

- `GET/POST /service-types/` - Service-Typen auflisten/erstellen
- `GET/PUT/DELETE /service-types/{id}/` - Service-Typ Details
- `GET/POST /services/` - Services auflisten/erstellen
- `GET/PUT/DELETE /services/{id}/` - Service Details
- `GET/POST /metrics/` - Metriken auflisten/erstellen
- `GET/PUT/DELETE /metrics/{id}/` - Metrik Details
- `GET/POST /incidents/` - Incidents auflisten/erstellen
- `GET/PUT/DELETE /incidents/{id}/` - Incident Details
- `GET/POST /reports/` - Reports auflisten/erstellen
- `GET/PUT/DELETE /reports/{id}/` - Report Details

### Data Sources API (`/api/v1/data-sources/`)

- `POST /csv/upload/` - CSV-Datei hochladen
- `GET /csv/status/{id}/` - Upload-Status
- `POST /csv/process/{id}/` - Hochgeladene CSV verarbeiten
- `GET /csv/history/` - Upload-Historie

## CSV Upload Format

### Erforderliche Felder

- `service_name` oder `service` - Name des Services
- Metrik-Felder (mindestens eines):
  - `availability` - Verfügbarkeit in Prozent
  - `response_time` - Antwortzeit in Millisekunden
  - `throughput` - Requests pro Sekunde
  - `error_rate` - Fehlerrate in Prozent

### Optionale Felder

- `timestamp` - Wann die Metrik aufgezeichnet wurde
- `uptime_seconds` - Gesamte Uptime in Sekunden
- `downtime_seconds` - Gesamte Downtime in Sekunden
- `total_requests` - Gesamtzahl der Requests
- `failed_requests` - Anzahl fehlgeschlagener Requests
- `unit` - Einheit der Messung
- `notes` - Zusätzliche Notizen

### Beispiel CSV

```csv
service_name,timestamp,availability,response_time,uptime_seconds,total_requests,failed_requests
Web API,2024-01-01 12:00:00,99.9,150,3590,1000,1
Database,2024-01-01 12:00:00,99.8,50,3588,500,1
```

## Entwicklung

### Hinzufügen neuer Metriken

1. Datenquelle in Admin-Interface erstellen
2. Feldzuordnungen für CSV-Spalten konfigurieren
3. CSV-Datei über API oder Admin hochladen
4. Hochgeladene Daten verarbeiten

### Modell-Erweiterungen

- Alle Modelle verwenden UUID-Primärschlüssel für Sicherheit
- Modelle enthalten created/updated Timestamps
- Beziehungen verwenden proper related_name Attribute
- Indizes sind für Performance konfiguriert

### API-Entwicklung

- Verwendet Django REST Framework mit ViewSets
- Enthält Filterung, Suche und Sortierung
- Umfassende Serializer für alle Modelle
- Proper Error Handling und Validierung

## Nächste Schritte

### Für Produktions-Deployment

1. PostgreSQL-Datenbank einrichten
2. Umgebungsvariablen konfigurieren
3. Redis für Caching einrichten
4. Celery für Background-Tasks konfigurieren
5. Monitoring und Logging einrichten
6. Email/Slack-Benachrichtigungen konfigurieren
7. Automatisierte Backups einrichten

### Frontend-Entwicklung

1. React/Vue.js Frontend erstellen
2. Dashboard-Visualisierungen implementieren
3. Real-time Updates mit WebSockets hinzufügen
4. Mobile-responsive Interface erstellen

### Zusätzliche Features

1. Real-time Metrik-Sammlung
2. Erweiterte Alerting mit ML
3. Multi-Tenant Support
4. API Rate Limiting
5. Erweiterte Reporting mit Charts
6. Integration mit Monitoring-Tools

## Architektur-Entscheidungen

### Datenbank-Design

- UUID-Primärschlüssel für Sicherheit und Verteilung
- Ordnungsgemäße Fremdschlüssel-Beziehungen mit Cascade-Optionen
- Indizes auf häufig abgefragten Feldern
- Datenbank-Routing für Multi-Source-Support

### API-Design

- RESTful-Endpunkte nach Django-Konventionen
- Umfassende Filterung und Suchfunktionen
- Ordnungsgemäße HTTP-Statuscodes und Fehlerbehandlung
- Paginierung für große Datensätze

### Sicherheitsüberlegungen

- Umgebungsbasierte Konfiguration
- Passwort-Felder als write-only markiert
- Ordnungsgemäße Benutzerauthentifizierung integriert
- CORS-Konfiguration für Frontend-Zugriff

### Performance-Optimierungen

- Datenbankabfrage-Optimierung mit select_related
- Ordnungsgemäße Indizierung auf Modellen
- Paginierung zur Handhabung großer Datensätze
- Datei-Upload-Größenlimits und Validierung

## Lizenz

Dieses Projekt ist für Bildungs- und Entwicklungszwecke erstellt.

## Kontakt

**Boiman Kupermann Solutions GmbH**

- Email: info@boiman-kupermann.com
- Website: https://boiman-kupermann.com

---

**⚠️ Hinweis**: Dies ist ein experimentelles Projekt der bks-lab Organisation. Für Produktionsanwendungen wird eine vollständige Validierung und Tests empfohlen.
