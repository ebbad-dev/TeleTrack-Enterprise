"""
TeleTrack Enterprise — Alert & Comment Models
Alert lifecycle management with collaborative comments.
"""

from extensions import db
from models.mixins import TimestampMixin, SoftDeleteMixin


class Alert(TimestampMixin, SoftDeleteMixin, db.Model):
    """Network alert with full lifecycle management."""

    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(
        db.Integer, db.ForeignKey("devices.id"), nullable=False, index=True
    )
    assigned_tech_id = db.Column(
        db.Integer, db.ForeignKey("technicians.id"), nullable=True, index=True
    )
    alert_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(
        db.String(30), default="medium", nullable=False, index=True
    )  # critical, high, medium, low
    message = db.Column(db.String(500))
    alert_time = db.Column(
        db.DateTime, default=db.func.now(), nullable=False, index=True
    )
    acknowledged_at = db.Column(db.DateTime)
    resolved_time = db.Column(db.DateTime)
    status = db.Column(
        db.String(30), default="open", nullable=False, index=True
    )  # open, assigned, in_progress, resolved, escalated, closed
    priority = db.Column(db.Integer, default=3)  # 1 = highest, 5 = lowest
    resolution_note = db.Column(db.Text)
    image_url = db.Column(db.String(500))

    # SLA tracking
    sla_policy_id = db.Column(db.Integer, db.ForeignKey("sla_policies.id"), nullable=True)
    sla_response_deadline = db.Column(db.DateTime)
    sla_resolution_deadline = db.Column(db.DateTime)
    sla_breached = db.Column(db.Boolean, default=False)

    # Who created / resolved
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Incident link
    incident_id = db.Column(db.Integer, db.ForeignKey("incidents.id"), nullable=True)

    # Relationships
    assigned_tech = db.relationship("Technician", foreign_keys=[assigned_tech_id])
    sla_policy = db.relationship("SLAPolicy", foreign_keys=[sla_policy_id])
    created_by = db.relationship("User", foreign_keys=[created_by_id])
    resolved_by = db.relationship("User", foreign_keys=[resolved_by_id])
    comments = db.relationship(
        "AlertComment",
        backref="alert",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="AlertComment.commented_at.desc()",
    )

    def __repr__(self):
        return f"<Alert #{self.id} [{self.severity}] {self.alert_type}>"

    def to_dict(self):
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device.device_name if self.device else None,
            "device_ip": self.device.ip_address if self.device else None,
            "assigned_tech_id": self.assigned_tech_id,
            "technician_name": self.assigned_tech.full_name if self.assigned_tech else "Unassigned",
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "alert_time": self.alert_time.isoformat() if self.alert_time else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_time": self.resolved_time.isoformat() if self.resolved_time else None,
            "status": self.status,
            "priority": self.priority,
            "resolution_note": self.resolution_note,
            "image_url": self.image_url,
            "sla_breached": self.sla_breached,
            "incident_id": self.incident_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AlertComment(db.Model):
    """Collaborative comments on alerts."""

    __tablename__ = "alert_comments"

    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(
        db.Integer, db.ForeignKey("alerts.id"), nullable=False, index=True
    )
    technician_id = db.Column(
        db.Integer, db.ForeignKey("technicians.id"), nullable=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    comment = db.Column(db.Text, nullable=False)
    comment_type = db.Column(
        db.String(30), default="note"
    )  # note, update, resolution, escalation
    commented_at = db.Column(
        db.DateTime, default=db.func.now(), nullable=False
    )

    # Relationships
    technician = db.relationship("Technician", foreign_keys=[technician_id])
    author = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        author_name = None
        if self.author:
            author_name = self.author.full_name
        elif self.technician:
            author_name = self.technician.full_name

        return {
            "id": self.id,
            "alert_id": self.alert_id,
            "author": author_name,
            "comment": self.comment,
            "comment_type": self.comment_type,
            "commented_at": self.commented_at.isoformat() if self.commented_at else None,
        }
