"""
Schemas para validación y serialización de productos.
"""
from flask import request


class ProductCreateSchema:
    """Schema para validar creación de productos"""
    
    @staticmethod
    def validate(data):
        errors = {}
        
        # Validar name (requerido)
        if not data.get('name') or not data['name'].strip():
            errors['name'] = 'El nombre es obligatorio'
        
        # Validar price (requerido, debe ser número positivo)
        try:
            price = float(data.get('price', 0))
            if price <= 0:
                errors['price'] = 'El precio debe ser mayor a 0'
            data['price'] = price
        except (ValueError, TypeError):
            errors['price'] = 'El precio debe ser un número válido'
        
        # Validar category_ids (requerido, al menos una)
        category_ids = data.get('category_ids', [])
        if not category_ids or len(category_ids) == 0:
            errors['category_ids'] = 'Debe seleccionar al menos una categoría'
        
        # Validar tag_ids (opcional, pero debe ser lista si existe)
        if 'tag_ids' not in data:
            data['tag_ids'] = []
        
        # Validar provider_ids (opcional, pero debe ser lista si existe)
        if 'provider_ids' not in data:
            data['provider_ids'] = []
        
        # Si hay errores, retornar None y el dict de errores
        if errors:
            return None, errors
        
        # Retornar datos validados
        return data, None


class ProductUpdateSchema:
    """Schema para validar actualización de productos"""
    
    @staticmethod
    def validate(data):
        errors = {}
        
        # Validar name (opcional en update, pero si viene debe tener valor)
        if 'name' in data:
            if not data['name'] or not data['name'].strip():
                errors['name'] = 'El nombre no puede estar vacío'
        
        # Validar price (opcional en update, pero si viene debe ser válido)
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    errors['price'] = 'El precio debe ser mayor a 0'
                data['price'] = price
            except (ValueError, TypeError):
                errors['price'] = 'El precio debe ser un número válido'
        
        # Si hay errores, retornar None y el dict de errores
        if errors:
            return None, errors
        
        return data, None


class ProductResponseSchema:
    """
    Schema para serializar productos en las respuestas.
    Maneja dos modos: público y admin.
    """
    
    @staticmethod
    def serialize(product, include_admin_fields=False):
        """
        Serializa un producto a diccionario.
        
        Args:
            product: Instancia del modelo Product
            include_admin_fields: Si True, incluye price y providers
        
        Returns:
            Dict con los datos del producto
        """
        # Construir URL de imagen
        image_url = None
        if product.image_path:
            base_url = request.host_url.rstrip('/')
            image_url = f"{base_url}/uploads/{product.image_path}"
        
        # Datos base (siempre se incluyen)
        data = {
            'id': product.id,
            'name': product.name,
            'description': product.description or '',
            'image_url': image_url,
            'categories': [
                {
                    'id': cat.id,
                    'name': cat.name
                } 
                for cat in product.categories
            ],
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name
                }
                for tag in product.tags
            ],
        }
        
        # Datos admin (solo si se solicitan)
        if include_admin_fields:
            data['price'] = float(product.price)
            data['provider_id'] = product.providers[0].id if product.providers else None
            data['providers'] = [
                {
                    'id': prov.id,
                    'name': prov.name,
                    'contact': prov.contact,
                    'phone': prov.phone
                }
                for prov in product.providers
            ]
        
        return data
    
    @staticmethod
    def serialize_many(products, include_admin_fields=False):
        """Serializa una lista de productos"""
        return [
            ProductResponseSchema.serialize(p, include_admin_fields) 
            for p in products
        ]