from datetime import datetime
from ..database import db


# ---------------------------------------------------------------------------
# Tablas de asociacion muchos-a-muchos
# ---------------------------------------------------------------------------

product_categories = db.Table(
    'product_categories',
    db.Column('product_id',  db.Integer, db.ForeignKey('products.id',   ondelete='CASCADE'), primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
)

product_tags = db.Table(
    'product_tags',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id',     db.Integer, db.ForeignKey('tags.id',     ondelete='CASCADE'), primary_key=True),
)

product_providers = db.Table(
    'product_providers',
    db.Column('product_id',  db.Integer, db.ForeignKey('products.id',  ondelete='CASCADE'), primary_key=True),
    db.Column('provider_id', db.Integer, db.ForeignKey('providers.id', ondelete='CASCADE'), primary_key=True),
)


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

class Product(db.Model):
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price       = db.Column(db.Numeric(12, 2), nullable=False)
    image_path  = db.Column(db.String(500), nullable=True)

    categories = db.relationship('Category', secondary=product_categories, backref='products')
    tags       = db.relationship('Tag',      secondary=product_tags,       backref='products')
    providers  = db.relationship('Provider', secondary=product_providers,  backref='products')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)