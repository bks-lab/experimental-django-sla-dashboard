"""
Database router for handling multiple data sources in the SLA dashboard.
Routes models to appropriate databases based on their app or model type.
"""

class DatabaseRouter:
    """
    A router to control all database operations on models for different
    databases. Routes SLA metrics and external data sources appropriately.
    """
    
    route_app_labels = {
        'sla_metrics': 'default',
        'data_sources': 'default', 
        'alerts': 'default',
        'dashboard': 'default',
        'auth': 'default',
        'contenttypes': 'default',
        'sessions': 'default',
        'admin': 'default',
    }

    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.route_app_labels:
            return self.route_app_labels[model._meta.app_label]
        return None

    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.route_app_labels:
            return self.route_app_labels[model._meta.app_label]
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        db_set = {'default', 'sqlite_fallback'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.route_app_labels:
            return db == self.route_app_labels[app_label]
        elif db == 'default':
            return True
        return False