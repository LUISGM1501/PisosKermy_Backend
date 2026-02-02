class ProviderCreateSchema:
    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors = {}

        # Campos obligatorios
        name = data.get('name')
        if name is None or not str(name).strip():
            errors['name'] = 'El nombre es requerido'
        elif len(str(name).strip()) > 200:
            errors['name'] = 'El nombre no puede superar 200 caracteres'

        # Campos opcionales con limites de largo
        contact = data.get('contact')
        if contact is not None and len(str(contact).strip()) > 200:
            errors['contact'] = 'El contacto no puede superar 200 caracteres'

        phone = data.get('phone')
        if phone is not None and len(str(phone).strip()) > 50:
            errors['phone'] = 'El telefono no puede superar 50 caracteres'

        if errors:
            return None, errors

        return {
            'name':        str(name).strip(),
            'contact':     str(contact).strip() if contact else None,
            'phone':       str(phone).strip() if phone else None,
            'description': str(data.get('description', '')).strip() if data.get('description') else None,
        }, None


class ProviderUpdateSchema:
    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors = {}
        cleaned = {}

        # Nombre es requerido si se envia
        if 'name' in data:
            name = data['name']
            if not str(name).strip():
                errors['name'] = 'El nombre no puede estar vacio'
            elif len(str(name).strip()) > 200:
                errors['name'] = 'El nombre no puede superar 200 caracteres'
            else:
                cleaned['name'] = str(name).strip()

        if 'contact' in data:
            contact = data['contact']
            if contact is not None and len(str(contact).strip()) > 200:
                errors['contact'] = 'El contacto no puede superar 200 caracteres'
            else:
                cleaned['contact'] = str(contact).strip() if contact else None

        if 'phone' in data:
            phone = data['phone']
            if phone is not None and len(str(phone).strip()) > 50:
                errors['phone'] = 'El telefono no puede superar 50 caracteres'
            else:
                cleaned['phone'] = str(phone).strip() if phone else None

        if 'description' in data:
            description = data['description']
            cleaned['description'] = str(description).strip() if description else None

        if errors:
            return None, errors

        if not cleaned:
            return None, {'general': 'No hay campos para actualizar'}

        return cleaned, None


class ProviderResponseSchema:
    @staticmethod
    def serialize(provider):
        return {
            'id':          provider.id,
            'name':        provider.name,
            'contact':     provider.contact,
            'phone':       provider.phone,
            'description': provider.description,
            'created_at':  provider.created_at.isoformat() if provider.created_at else None,
            'updated_at':  provider.updated_at.isoformat() if provider.updated_at else None,
        }

    @staticmethod
    def serialize_many(providers):
        return [ProviderResponseSchema.serialize(p) for p in providers]