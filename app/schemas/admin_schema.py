"""Schemas de validacion para el modelo Admin."""


class AdminCreateSchema:
    """Schema para crear un nuevo admin."""

    @staticmethod
    def validate(data):
        """Valida los datos para crear un admin.
        
        Returns:
            Tupla (validated_data, errors)
        """
        if not data:
            return None, {'_error': 'Datos requeridos'}

        errors = {}

        # Email
        email = data.get('email', '').strip()
        if not email:
            errors['email'] = 'Email es requerido'
        elif '@' not in email or '.' not in email.split('@')[-1]:
            errors['email'] = 'Email invalido'

        # Name
        name = data.get('name', '').strip()
        if not name:
            errors['name'] = 'Nombre es requerido'
        elif len(name) < 2:
            errors['name'] = 'Nombre debe tener al menos 2 caracteres'

        # Password
        password = data.get('password', '').strip()
        if not password:
            errors['password'] = 'Password es requerido'
        elif len(password) < 6:
            errors['password'] = 'Password debe tener al menos 6 caracteres'

        if errors:
            return None, errors

        return {
            'email': email.lower(),
            'name': name,
            'password': password
        }, None


class AdminUpdateSchema:
    """Schema para actualizar un admin."""

    @staticmethod
    def validate(data):
        """Valida los datos para actualizar un admin.
        
        Returns:
            Tupla (validated_data, errors)
        """
        if not data:
            return None, {'_error': 'Datos requeridos'}

        errors = {}
        validated = {}

        # Email (opcional)
        if 'email' in data:
            email = data['email'].strip()
            if not email:
                errors['email'] = 'Email no puede estar vacio'
            elif '@' not in email or '.' not in email.split('@')[-1]:
                errors['email'] = 'Email invalido'
            else:
                validated['email'] = email.lower()

        # Name (opcional)
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                errors['name'] = 'Nombre no puede estar vacio'
            elif len(name) < 2:
                errors['name'] = 'Nombre debe tener al menos 2 caracteres'
            else:
                validated['name'] = name

        # Debe actualizar al menos un campo
        if not validated and not errors:
            errors['_error'] = 'Debe proporcionar al menos un campo para actualizar'

        if errors:
            return None, errors

        return validated, None


class AdminPasswordSchema:
    """Schema para cambiar password."""

    @staticmethod
    def validate(data):
        """Valida los datos para cambiar password.
        
        Returns:
            Tupla (validated_data, errors)
        """
        if not data:
            return None, {'_error': 'Datos requeridos'}

        errors = {}

        password = data.get('password', '').strip()
        if not password:
            errors['password'] = 'Password es requerido'
        elif len(password) < 6:
            errors['password'] = 'Password debe tener al menos 6 caracteres'

        if errors:
            return None, errors

        return {'password': password}, None


class AdminResponseSchema:
    """Schema para serializar respuestas de Admin."""

    @staticmethod
    def serialize(admin):
        """Serializa un admin a dict."""
        return {
            'id': admin.id,
            'email': admin.email,
            'name': admin.name,
            'is_active': admin.is_active,
            'created_at': admin.created_at.isoformat() if admin.created_at else None,
        }

    @staticmethod
    def serialize_many(admins):
        """Serializa una lista de admins."""
        return [AdminResponseSchema.serialize(admin) for admin in admins]