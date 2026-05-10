"""
TeleTrack Enterprise — Request Logger Middleware
Logs all API requests with timing information.
"""

import time
import logging
from flask import request, g

logger = logging.getLogger("teletrack.requests")


def register_request_logger(app):
    """Register request/response logging middleware."""

    @app.before_request
    def before_request():
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            duration = round((time.time() - g.start_time) * 1000, 2)
        else:
            duration = 0

        # Skip health check and static file logging
        if request.path in ("/health", "/api/health") or request.path.startswith("/static"):
            return response

        log_data = {
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": duration,
            "ip": request.remote_addr,
        }

        if response.status_code >= 500:
            logger.error(f"[{log_data['method']}] {log_data['path']} → {log_data['status']} ({log_data['duration_ms']}ms)")
        elif response.status_code >= 400:
            logger.warning(f"[{log_data['method']}] {log_data['path']} → {log_data['status']} ({log_data['duration_ms']}ms)")
        else:
            logger.info(f"[{log_data['method']}] {log_data['path']} → {log_data['status']} ({log_data['duration_ms']}ms)")

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration}ms"

        return response
