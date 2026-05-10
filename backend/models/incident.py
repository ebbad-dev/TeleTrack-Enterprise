"""
TeleTrack Enterprise — Incident Management Models
Full incident lifecycle with timeline, escalation, and RCA.
"""

from extensions import db
from models.mixins import TimestampMixin, SoftDeleteMixin


class Incident(TimestampMixin, SoftDeleteMixin, db.Model):
    """Incident tracking with full lifecycle management."""

    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(
        db.String(30), default="medium", nullable=False, index=True
    )  # critical, high, medium, low
    status = db.Column(
        db.String(30), default="open", nullable=False, index=True
    )  # open, acknowledged, investigating, resolved, escalated, closed
    priority = db.Column(db.Integer, default=3)
    impact = db.Column(db.String(50))  # critical, major, minor, none
    affected_services = db.Column(db.Text)

    # Ownership
    reported_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=True)

    # Timestamps
    reported_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)

    # SLA
    sla_policy_id = db.Column(db.Integer, db.ForeignKey("sla_policies.id"), nullable=True)
    sla_response_deadline = db.Column(db.DateTime)
    sla_resolution_deadline = db.Column(db.DateTime)
    sla_breached = db.Column(db.Boolean, default=False)

    # Root Cause Analysis
    root_cause = db.Column(db.Text)
    resolution_summary = db.Column(db.Text)
    lessons_learned = db.Column(db.Text)

    # Relationships
    reported_by = db.relationship("User", foreign_keys=[reported_by_id])
    assigned_to = db.relationship("User", foreign_keys=[assigned_to_id])
    team = db.relationship("Team", foreign_keys=[team_id])
    timeline = db.relationship(
        "IncidentTimeline",
        backref="incident",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="IncidentTimeline.timestamp.asc()",
    )
    escalations = db.relationship(
        "Escalation",
        backref="incident",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    alerts = db.relationship("Alert", backref="incident", lazy="dynamic")
    attachments = db.relationship(
        "FileAttachment",
        backref="incident",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Incident #{self.id} [{self.severity}] {self.title[:40]}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "priority": self.priority,
            "impact": self.impact,
            "affected_services": self.affected_services,
            "reported_by": self.reported_by.full_name if self.reported_by else None,
            "assigned_to": self.assigned_to.full_name if self.assigned_to else None,
            "reported_at": self.reported_at.isoformat() if self.reported_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "sla_breached": self.sla_breached,
            "root_cause": self.root_cause,
            "resolution_summary": self.resolution_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IncidentTimeline(db.Model):
    """Timeline of actions taken on an incident."""

    __tablename__ = "incident_timeline"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True
    )
    action = db.Column(db.String(100), nullable=False)  # created, assigned, escalated, resolved, etc.
    description = db.Column(db.Text)
    performed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Relationships
    performed_by = db.relationship("User", foreign_keys=[performed_by_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "action": self.action,
            "description": self.description,
            "performed_by": self.performed_by.full_name if self.performed_by else "System",
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class Escalation(db.Model):
    """Escalation rules and history."""

    __tablename__ = "escalations"

    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(
        db.Integer, db.ForeignKey("incidents.id"), nullable=False, index=True
    )
    from_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reason = db.Column(db.Text, nullable=False)
    escalation_level = db.Column(db.Integer, default=1)  # 1, 2, 3 tier
    escalated_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Relationships
    from_user = db.relationship("User", foreign_keys=[from_user_id])
    to_user = db.relationship("User", foreign_keys=[to_user_id])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "from_user": self.from_user.full_name if self.from_user else None,
            "to_user": self.to_user.full_name if self.to_user else None,
            "reason": self.reason,
            "escalation_level": self.escalation_level,
            "escalated_at": self.escalated_at.isoformat() if self.escalated_at else None,
        }
