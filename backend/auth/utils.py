"""
TeleTrack Enterprise — Authentication Utilities
Password hashing, JWT helpers, and security functions.
"""

import bcrypt
import secrets
import hashlib
from flask_jwt_extended import get_jwt_identity


def current_user_id() -> int:
    """Get the current user's integer ID from the JWT token."""
    return int(get_jwt_identity())
from datetime import datetime, timezone


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def generate_api_key() -> tuple:
    """Generate an API key and return (full_key, prefix, key_hash)."""
    full_key = f"tt_{secrets.token_urlsafe(32)}"
    prefix = full_key[:10]
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, prefix, key_hash


def generate_reset_token() -> str:
    """Generate a secure password reset token."""
    return secrets.token_urlsafe(48)


def is_strong_password(password: str) -> tuple:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, None
