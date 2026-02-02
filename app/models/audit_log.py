from datetime import datetime
from ..database import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id          = db.Column(db.Integer, primary_key=True)
    admin_id    = db.Column(db.Integer, db.ForeignKey('admins.id'))
    action      = db.Column(db.String(50), nullable=False)       # LOGIN | LOGOUT | CREATE | UPDATE | DELETE
    entity      = db.Column(db.String(50))                       # category | tag | product | ...
    entity_id   = db.Column(db.Integer)
    details     = db.Column(db.JSON)
    ip_address  = db.Column(db.String(45))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    admin = db.relationship('Admin', backref='audit_logs')