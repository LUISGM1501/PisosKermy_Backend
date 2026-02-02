class CategoryCreateSchema:
    """Valida la entrada para crear una categoria."""

    @staticmethod
    def validate(data):
        """
        Retorna (datos_limpios, errores).
        Si la validacion falla: datos_limpios es None.
        Si pasa: errores es None.
        """
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors = {}

        name = data.get('name')
        if name is None or not str(name).strip():
            errors['name'] = 'El nombre es requerido'
        elif len(str(name).strip()) > 100:
            errors['name'] = 'El nombre no puede superar 100 caracteres'

        if errors:
            return None, errors

        return {'name': str(name).strip()}, None


class CategoryUpdateSchema:
    """Valida la entrada para editar una categoria."""

    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors = {}

        name = data.get('name')
        if name is None or not str(name).strip():
            errors['name'] = 'El nombre es requerido'
        elif len(str(name).strip()) > 100:
            errors['name'] = 'El nombre no puede superar 100 caracteres'

        if errors:
            return None, errors

        return {'name': str(name).strip()}, None


class CategoryResponseSchema:
    """Serializa un modelo Category a diccionario para la respuesta HTTP."""

    @staticmethod
    def serialize(category):
        return {
            'id':         category.id,
            'name':       category.name,
            'created_at': category.created_at.isoformat() if category.created_at else None,
            'updated_at': category.updated_at.isoformat() if category.updated_at else None,
        }

    @staticmethod
    def serialize_many(categories):
        return [CategoryResponseSchema.serialize(c) for c in categories]