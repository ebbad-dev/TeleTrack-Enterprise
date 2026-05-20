"""
TeleTrack Enterprise — Authentication Routes
JWT-based authentication with login, register, refresh, and password management.
"""

from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from extensions import db, limiter
from models.user import User, UserSession, LoginHistory
from auth.utils import hash_password, verify_password, is_strong_password
from auth.decorators import get_current_user, admin_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ═══════════════════════════════════════════════════════════════════
# LOGIN
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10/minute")
def login():
    """Authenticate user and return JWT tokens."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body required"}), 400

    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400

    # Find user
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    # Log attempt
    log = LoginHistory(
        username=username,
        ip_address=request.remote_addr,
        user_agent=request.headers.get("User-Agent", "")[:500],
    )

    if not user:
        log.success = False
        log.failure_reason = "User not found"
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    if user.is_deleted:
        log.user_id = user.id
        log.success = False
        log.failure_reason = "Account deleted"
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": False, "error": "Account has been deactivated"}), 401

    if user.is_locked:
        log.user_id = user.id
        log.success = False
        log.failure_reason = "Account locked"
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": False, "error": "Account temporarily locked. Try again later."}), 423

    if user.status != "active":
        log.user_id = user.id
        log.success = False
        log.failure_reason = f"Account status: {user.status}"
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": False, "error": f"Account is {user.status}"}), 403

    if not verify_password(password, user.password_hash):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        # Lock after 5 failed attempts
        if user.failed_login_attempts >= 5:
            from datetime import timedelta
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=15)

        log.user_id = user.id
        log.success = False
        log.failure_reason = "Invalid password"
        db.session.add(log)
        db.session.commit()
        return jsonify({"success": False, "error": "Invalid credentials"}), 401

    # Success — generate tokens
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "roles": [r.name for r in user.roles],
        },
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    # Update user
    user.last_login = datetime.now(timezone.utc)
    user.failed_login_attempts = 0
    user.locked_until = None

    # Log success
    log.user_id = user.id
    log.success = True
    db.session.add(log)
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict(include_permissions=True),
        }
    )


# ═══════════════════════════════════════════════════════════════════
# REGISTER (Admin only)
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/register", methods=["POST"])
@jwt_required()
@admin_required
def register():
    """Register a new user (admin only)."""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "Request body required"}), 400

    required = ["username", "email", "password", "full_name"]
    for field in required:
        if not data.get(field):
            return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

    username = data["username"].strip().lower()
    email = data["email"].strip().lower()

    # Check duplicates
    if User.query.filter_by(username=username).first():
        return jsonify({"success": False, "error": "Username already exists"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "error": "Email already registered"}), 409

    # Validate password
    valid, error = is_strong_password(data["password"])
    if not valid:
        return jsonify({"success": False, "error": error}), 400

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(data["password"]),
        full_name=data["full_name"],
        phone=data.get("phone"),
        status="active",
    )

    # Assign roles
    from models.user import Role
    role_names = data.get("roles", ["noc_operator"])
    for role_name in role_names:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    return jsonify(
        {"success": True, "message": "User registered successfully", "user": user.to_dict()}
    ), 201


# ═══════════════════════════════════════════════════════════════════
# TOKEN REFRESH
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.is_active:
        return jsonify({"success": False, "error": "Invalid user"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "username": user.username,
            "roles": [r.name for r in user.roles],
        },
    )

    return jsonify({"success": True, "access_token": access_token})


# ═══════════════════════════════════════════════════════════════════
# CURRENT USER
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Get current authenticated user's profile."""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    return jsonify({"success": True, "user": user.to_dict(include_permissions=True)})


# ═══════════════════════════════════════════════════════════════════
# CHANGE PASSWORD
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change the current user's password."""
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404

    data = request.get_json()
    current_password = data.get("current_password")
    new_password = data.get("new_password")

    if not current_password or not new_password:
        return jsonify({"success": False, "error": "Both current and new password required"}), 400

    if not verify_password(current_password, user.password_hash):
        return jsonify({"success": False, "error": "Current password is incorrect"}), 401

    valid, error = is_strong_password(new_password)
    if not valid:
        return jsonify({"success": False, "error": error}), 400

    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully"})


# ═══════════════════════════════════════════════════════════════════
# LOGOUT
# ═══════════════════════════════════════════════════════════════════


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Revoke the current access token."""
    from flask import current_app
    jti = get_jwt()["jti"]

    # Add to in-memory blocklist
    blocklist = current_app.config.get('TOKEN_BLOCKLIST', set())
    blocklist.add(jti)

    # Also mark session in DB if it exists
    session = UserSession.query.filter_by(jti=jti).first()
    if session:
        session.revoked = True
        session.revoked_at = datetime.now(timezone.utc)
        db.session.commit()

    return jsonify({"success": True, "message": "Logged out successfully"})
