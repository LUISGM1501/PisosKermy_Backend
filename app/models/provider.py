from datetime import datetime
from ..database import db


class Provider(db.Model):
    __tablename__ = 'providers'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    contact     = db.Column(db.String(200), nullable=True)
    phone       = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)