import os

# ---------------------------------------------------------
# Superset-specific Config
# ---------------------------------------------------------
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'mysecretkey')

# Enable authentication and security settings
AUTH_TYPE = 1  # Database authentication

# Enable Cross-Origin Resource Sharing (CORS)
ENABLE_CORS = True

# Allow Public Dashboards
PUBLIC_ROLE_LIKE = "Gamma"

# Enable Row Level Security
ENABLE_ROW_LEVEL_SECURITY = True

# ---------------------------------------------------------
# Database Connection Config (ClickHouse)
# ---------------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'clickhouse://default:default@clickhouse:8123/default'

# ---------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------
FEATURE_FLAGS = {
    "ALERT_REPORTS": False,  # Disable Email Alerts (since no Celery)
    "DASHBOARD_RBAC": True,  # Role-based Dashboard Access
    "THUMBNAILS": False,     # Disable Thumbnails (since no Celery)
    "ENABLE_TEMPLATE_PROCESSING": True,  # Enable Jinja Templating
}

# # ---------------------------------------------------------
# # Logging
# # ---------------------------------------------------------
# LOGGING_CONFIGURATOR = None
