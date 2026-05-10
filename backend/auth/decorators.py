"""
TeleTrack Enterprise — Authentication Decorators
Custom decorators for role and permission enforcement.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models.user import User


def _get_user_from_jwt():
    """Helper to get user from JWT identity (string -> int conversion)."""
    user_id = get_jwt_identity()
    return User.query.get(int(user_id))


def role_required(*roles):
    """
    Decorator that requires the user to have at least one of the specified roles.
    Usage: @role_required('super_admin', 'network_admin')
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = _get_user_from_jwt()

            if not user or not user.is_active:
                return jsonify({"success": False, "error": "Account inactive or not found"}), 403

            if not any(user.has_role(role) for role in roles):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Insufficient role. Required: {', '.join(roles)}",
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def permission_required(*permissions):
    """
    Decorator that requires the user to have all specified permissions.
    Usage: @permission_required('devices:write', 'devices:delete')
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = _get_user_from_jwt()

            if not user or not user.is_active:
                return jsonify({"success": False, "error": "Account inactive or not found"}), 403

            missing = [p for p in permissions if not user.has_permission(p)]
            if missing:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Missing permissions: {', '.join(missing)}",
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn):
    """Shorthand decorator requiring super_admin or network_admin role."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = _get_user_from_jwt()

        if not user or not user.is_active:
            return jsonify({"success": False, "error": "Account inactive"}), 403

        if not (user.has_role("super_admin") or user.has_role("network_admin") or user.has_role("admin")):
            return jsonify({"success": False, "error": "Admin access required"}), 403

        return fn(*args, **kwargs)

    return wrapper


def get_current_user():
    """Helper to get the current authenticated user from JWT."""
    try:
        return _get_user_from_jwt()
    except Exception:
        return None
