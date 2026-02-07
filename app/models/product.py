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
    image_path  = db.Column(db.String(500), nullable=True)  # DEPRECATED: Mantener por compatibilidad, usar images

    categories = db.relationship('Category', secondary=product_categories, backref='products')
    tags       = db.relationship('Tag',      secondary=product_tags,       backref='products')
    providers  = db.relationship('Provider', secondary=product_providers,  backref='products')
    
    # NUEVO: Relación con ProductImage
    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan', 
                            order_by='ProductImage.display_order')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def primary_image(self):
        """Retorna la imagen principal del producto"""
        for img in self.images:
            if img.is_primary:
                return img
        # Si no hay imagen principal, retornar la primera
        return self.images[0] if self.images else None

    @property
    def image_url(self):
        """
        Propiedad de compatibilidad.
        Retorna la URL de la imagen principal.
        """
        primary = self.primary_image
        if primary:
            from ..utils.file import get_image_url
            return get_image_url(primary.image_path)
        # Fallback a image_path legacy
        if self.image_path:
            from ..utils.file import get_image_url
            return get_image_url(self.image_path)
        return None