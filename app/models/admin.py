from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..database import db


class Admin(db.Model):
    __tablename__ = 'admins'

    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(200), unique=True, nullable=False)
    password_hash  = db.Column(db.String(256), nullable=False)
    name           = db.Column(db.String(200), nullable=False)
    is_active      = db.Column(db.Boolean, default=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)