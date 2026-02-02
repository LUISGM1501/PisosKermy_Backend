class TagCreateSchema:
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


class TagUpdateSchema:
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


class TagResponseSchema:
    @staticmethod
    def serialize(tag):
        return {
            'id':         tag.id,
            'name':       tag.name,
            'created_at': tag.created_at.isoformat() if tag.created_at else None,
            'updated_at': tag.updated_at.isoformat() if tag.updated_at else None,
        }

    @staticmethod
    def serialize_many(tags):
        return [TagResponseSchema.serialize(t) for t in tags]