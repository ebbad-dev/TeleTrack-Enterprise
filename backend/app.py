"""
TeleTrack Enterprise — Flask Application Factory
Central app creation with all extensions, middleware, and blueprints.
"""

import os
import sys
import logging
from flask import Flask, jsonify

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from extensions import db, jwt, cors, limiter, migrate, socketio
from middleware.error_handler import register_error_handlers
from middleware.request_logger import register_request_logger
from routes import register_blueprints
from auth.routes import auth_bp


def create_app(config_class=None):
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # ─── Setup Logging ────────────────────────────────────────────
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )
    logger = logging.getLogger("teletrack")
    logger.setLevel(log_level)

    # ─── Initialize Extensions ────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", ["*"])}})

    limiter.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode="threading")

    # ─── JWT Callbacks ────────────────────────────────────────────
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token(error):
        return jsonify({"success": False, "error": "Invalid token"}), 401

    @jwt.unauthorized_loader
    def missing_token(error):
        return jsonify({"success": False, "error": "Authorization token required"}), 401

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return jsonify({"success": False, "error": "Token has been revoked"}), 401

    # Token blocklist check (for logout/revocation support)
    @jwt.token_in_blocklist_loader
    def check_token_blocklist(jwt_header, jwt_payload):
        # For now, don't block any tokens - full session tracking comes with Redis
        return False

    # ─── Register Error Handlers ──────────────────────────────────
    register_error_handlers(app)

    # ─── Register Request Logger ──────────────────────────────────
    register_request_logger(app)

    # ─── Register Blueprints ──────────────────────────────────────
    app.register_blueprint(auth_bp)
    register_blueprints(app)

    # ─── Prometheus Monitoring Middleware ──────────────────────────
    from utils.metrics import init_metrics_middleware
    init_metrics_middleware(app)

    # ─── Health Check ─────────────────────────────────────────────
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "success": True,
            "status": "healthy",
            "service": "TeleTrack Enterprise",
            "version": "5.0.0",
        })

    # ─── Create tables (dev only) ─────────────────────────────────
    with app.app_context():
        # Import all models so SQLAlchemy knows about them
        import models  # noqa: F401

    # ─── WebSocket Events ─────────────────────────────────────────
    from flask_socketio import join_room, leave_room

    @socketio.on("connect")
    def handle_connect():
        logger.info("WebSocket client connected")

    @socketio.on("join")
    def handle_join(data):
        """Join user-specific room for targeted notifications."""
        room = data.get("room")
        if room:
            join_room(room)
            logger.debug(f"Client joined room: {room}")

    @socketio.on("subscribe_dashboard")
    def handle_dashboard_subscribe():
        """Subscribe to real-time dashboard updates."""
        join_room("dashboard")

    logger.info("TeleTrack Enterprise backend initialized successfully")
    return app
