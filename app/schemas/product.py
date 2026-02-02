class ProductCreateSchema:
    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors = {}

        # name — obligatorio
        name = data.get('name')
        if name is None or not str(name).strip():
            errors['name'] = 'El nombre es requerido'
        elif len(str(name).strip()) > 200:
            errors['name'] = 'El nombre no puede superar 200 caracteres'

        # price — obligatorio, numero no negativo
        price = data.get('price')
        if price is None:
            errors['price'] = 'El precio es requerido'
        else:
            try:
                price_val = float(price)
                if price_val < 0:
                    errors['price'] = 'El precio no puede ser negativo'
            except (ValueError, TypeError):
                errors['price'] = 'El precio debe ser un numero'

        # category_ids — lista opcional de enteros
        category_ids = data.get('category_ids', [])
        if not isinstance(category_ids, list):
            errors['category_ids'] = 'Debe ser una lista'
        elif not all(isinstance(i, int) for i in category_ids):
            errors['category_ids'] = 'Cada elemento debe ser un entero'

        # tag_ids — lista opcional de enteros
        tag_ids = data.get('tag_ids', [])
        if not isinstance(tag_ids, list):
            errors['tag_ids'] = 'Debe ser una lista'
        elif not all(isinstance(i, int) for i in tag_ids):
            errors['tag_ids'] = 'Cada elemento debe ser un entero'

        # provider_ids — lista opcional de enteros
        provider_ids = data.get('provider_ids', [])
        if not isinstance(provider_ids, list):
            errors['provider_ids'] = 'Debe ser una lista'
        elif not all(isinstance(i, int) for i in provider_ids):
            errors['provider_ids'] = 'Cada elemento debe ser un entero'

        if errors:
            return None, errors

        return {
            'name':         str(name).strip(),
            'description':  str(data['description']).strip() if data.get('description') else None,
            'price':        float(price),
            'category_ids': category_ids,
            'tag_ids':      tag_ids,
            'provider_ids': provider_ids,
        }, None


class ProductUpdateSchema:
    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors  = {}
        cleaned = {}

        if 'name' in data:
            name = data['name']
            if not str(name).strip():
                errors['name'] = 'El nombre no puede estar vacio'
            elif len(str(name).strip()) > 200:
                errors['name'] = 'El nombre no puede superar 200 caracteres'
            else:
                cleaned['name'] = str(name).strip()

        if 'description' in data:
            cleaned['description'] = str(data['description']).strip() if data['description'] else None

        if 'price' in data:
            try:
                price_val = float(data['price'])
                if price_val < 0:
                    errors['price'] = 'El precio no puede ser negativo'
                else:
                    cleaned['price'] = price_val
            except (ValueError, TypeError):
                errors['price'] = 'El precio debe ser un numero'

        if 'category_ids' in data:
            category_ids = data['category_ids']
            if not isinstance(category_ids, list):
                errors['category_ids'] = 'Debe ser una lista'
            elif not all(isinstance(i, int) for i in category_ids):
                errors['category_ids'] = 'Cada elemento debe ser un entero'
            else:
                cleaned['category_ids'] = category_ids

        if 'tag_ids' in data:
            tag_ids = data['tag_ids']
            if not isinstance(tag_ids, list):
                errors['tag_ids'] = 'Debe ser una lista'
            elif not all(isinstance(i, int) for i in tag_ids):
                errors['tag_ids'] = 'Cada elemento debe ser un entero'
            else:
                cleaned['tag_ids'] = tag_ids

        if 'provider_ids' in data:
            provider_ids = data['provider_ids']
            if not isinstance(provider_ids, list):
                errors['provider_ids'] = 'Debe ser una lista'
            elif not all(isinstance(i, int) for i in provider_ids):
                errors['provider_ids'] = 'Cada elemento debe ser un entero'
            else:
                cleaned['provider_ids'] = provider_ids

        if errors:
            return None, errors

        if not cleaned:
            return None, {'general': 'No hay campos para actualizar'}

        return cleaned, None


class ProductResponseSchema:
    @staticmethod
    def serialize(product, include_admin_fields=False):
        """
        include_admin_fields=False -> respuesta publica (sin precio ni proveedores)
        include_admin_fields=True  -> respuesta del admin (precio y proveedores incluidos)
        """
        from .category import CategoryResponseSchema
        from .tag import TagResponseSchema
        from .provider import ProviderResponseSchema

        data = {
            'id':          product.id,
            'name':        product.name,
            'description': product.description,
            'image_path':  product.image_path,
            'categories':  CategoryResponseSchema.serialize_many(product.categories),
            'tags':        TagResponseSchema.serialize_many(product.tags),
            'created_at':  product.created_at.isoformat() if product.created_at else None,
            'updated_at':  product.updated_at.isoformat() if product.updated_at else None,
        }

        if include_admin_fields:
            data['price']     = float(product.price) if product.price else None
            data['providers'] = ProviderResponseSchema.serialize_many(product.providers)

        return data

    @staticmethod
    def serialize_many(products, include_admin_fields=False):
        return [ProductResponseSchema.serialize(p, include_admin_fields) for p in products]