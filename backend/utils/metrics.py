"""
TeleTrack Enterprise — Prometheus Monitoring Middleware
Exposes application and system metrics for scraping.
"""

import time
from flask import request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Metrics definitions
REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 'HTTP Request Latency',
    ['method', 'endpoint']
)

def init_metrics_middleware(app):
    """Register hooks to track metrics for every request."""
    
    @app.before_request
    def start_timer():
        request._start_time = time.time()

    @app.after_request
    def record_metrics(response):
        if hasattr(request, '_start_time'):
            latency = time.time() - request._start_time
            # Get endpoint name or path
            endpoint = request.endpoint or request.path
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=response.status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(latency)
            
        return response

    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint."""
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
