"""
TeleTrack Enterprise — User, Role & Permission Models
Implements RBAC with granular permission control.
"""

from datetime import datetime, timezone
from extensions import db
from models.mixins import TimestampMixin, SoftDeleteMixin

# ═══════════════════════════════════════════════════════════════════
# Junction Tables
# ═══════════════════════════════════════════════════════════════════

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column(
        "permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True
    ),
)


# ═══════════════════════════════════════════════════════════════════
# Permission Model
# ═══════════════════════════════════════════════════════════════════


class Permission(db.Model):
    """Granular permission like 'devices:read', 'alerts:write', etc."""

    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # e.g. 'devices:read'
    description = db.Column(db.String(255))
    resource = db.Column(db.String(50), nullable=False)  # e.g. 'devices'
    action = db.Column(db.String(50), nullable=False)  # e.g. 'read'

    def __repr__(self):
        return f"<Permission {self.name}>"

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


# ═══════════════════════════════════════════════════════════════════
# Role Model
# ═══════════════════════════════════════════════════════════════════


class Role(db.Model):
    """Role with associated permissions."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    is_system = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    permissions = db.relationship(
        "Permission", secondary=role_permissions, backref="roles", lazy="joined"
    )

    def __repr__(self):
        return f"<Role {self.name}>"

    def has_permission(self, permission_name):
        return any(p.name == permission_name for p in self.permissions)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "is_system": self.is_system,
            "permissions": [p.name for p in self.permissions],
        }


# ═══════════════════════════════════════════════════════════════════
# User Model
# ═══════════════════════════════════════════════════════════════════


class User(TimestampMixin, SoftDeleteMixin, db.Model):
    """System user with authentication and RBAC."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(30))
    avatar_url = db.Column(db.String(500))
    status = db.Column(
        db.String(20), default="active", nullable=False, index=True
    )  # active, inactive, suspended
    last_login = db.Column(db.DateTime)
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    email_verified = db.Column(db.Boolean, default=False)
    must_change_password = db.Column(db.Boolean, default=False)

    # Relationships
    roles = db.relationship(
        "Role", secondary=user_roles, backref="users", lazy="joined"
    )
    login_history = db.relationship(
        "LoginHistory", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    api_keys = db.relationship(
        "APIKey", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )
    sessions = db.relationship(
        "UserSession", backref="user", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def is_active(self):
        return self.status == "active" and not self.is_deleted

    @property
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.now(timezone.utc):
            return True
        return False

    def has_role(self, role_name):
        return any(r.name == role_name for r in self.roles)

    def has_permission(self, permission_name):
        # Admin bypass
        if self.has_role("admin") or self.has_role("super_admin"):
            return True
            
        return any(
            r.has_permission(permission_name)
            for r in self.roles
        )

    @property
    def all_permissions(self):
        perms = set()
        for role in self.roles:
            for perm in role.permissions:
                perms.add(perm.name)
        return list(perms)

    def to_dict(self, include_permissions=False):
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "status": self.status,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "email_verified": self.email_verified,
            "roles": [r.to_dict() for r in self.roles],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_permissions:
            data["permissions"] = self.all_permissions
        return data


# ═══════════════════════════════════════════════════════════════════
# User Session (JWT Token Tracking)
# ═══════════════════════════════════════════════════════════════════


class UserSession(db.Model):
    """Tracks active JWT sessions for revocation support."""

    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=False)  # access, refresh
    issued_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)
    revoked_at = db.Column(db.DateTime)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))


# ═══════════════════════════════════════════════════════════════════
# API Key
# ═══════════════════════════════════════════════════════════════════


class APIKey(TimestampMixin, db.Model):
    """API keys for programmatic access."""

    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    key_hash = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    prefix = db.Column(db.String(10), nullable=False)  # first 8 chars for identification
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)


# ═══════════════════════════════════════════════════════════════════
# Login History
# ═══════════════════════════════════════════════════════════════════


class LoginHistory(db.Model):
    """Tracks all login attempts (successful and failed)."""

    __tablename__ = "login_history"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    username = db.Column(db.String(100))
    success = db.Column(db.Boolean, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    failure_reason = db.Column(db.String(255))
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
