"""
Metrics and Monitoring
=====================

Prometheus metrics setup and collection.
"""

from prometheus_client import Counter, Histogram, Gauge, Info
import structlog

logger = structlog.get_logger(__name__)

# Metrics definitions
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

DATABASE_CONNECTIONS = Gauge(
    'database_connections_active',
    'Active database connections',
    ['database_type']
)

APPLICATION_INFO = Info(
    'application',
    'Application information'
)


def setup_metrics():
    """Setup application metrics."""
    try:
        APPLICATION_INFO.info({
            'version': '1.0.0',
            'name': 'FastAPI Cloud Template'
        })
        logger.info("✅ Metrics collection initialized")
    except Exception as e:
        logger.error("❌ Failed to setup metrics", error=str(e))


def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record request metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
