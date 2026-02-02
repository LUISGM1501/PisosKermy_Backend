from datetime import datetime
from ..database import db


class SiteContent(db.Model):
    __tablename__ = 'site_content'

    id         = db.Column(db.Integer, primary_key=True)
    key        = db.Column(db.String(100), unique=True, nullable=False)  # ej: 'about_us'
    title      = db.Column(db.String(200), nullable=True)
    content    = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=True)

    admin = db.relationship('Admin')