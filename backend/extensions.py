"""
TeleTrack Enterprise — Flask Extension Initialization
Lazy-initialized extensions for the Flask app factory pattern.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO
from flask_migrate import Migrate

# ═══════════════════════════════════════════════════════════════════
# Extension Instances (initialized without app — bound in create_app)
# ═══════════════════════════════════════════════════════════════════

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
migrate = Migrate()
socketio = SocketIO()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour"],
    storage_uri="memory://",
)
