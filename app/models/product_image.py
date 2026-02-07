from datetime import datetime
from ..database import db


class ProductImage(db.Model):
    """
    Modelo para almacenar múltiples imágenes por producto.
    Cada producto puede tener varias imágenes, una de ellas marcada como principal.
    """
    __tablename__ = 'product_images'

    id            = db.Column(db.Integer, primary_key=True)
    product_id    = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_path    = db.Column(db.String(500), nullable=False)
    is_primary    = db.Column(db.Boolean, default=False, nullable=False)  # Imagen principal
    display_order = db.Column(db.Integer, default=0, nullable=False)       # Orden de visualización
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con Product
    product = db.relationship('Product', back_populates='images')

    def __repr__(self):
        return f'<ProductImage {self.id} - Product {self.product_id} - Primary: {self.is_primary}>'