from ..repositories.admin_repository import AdminRepository
from ..utils.errors import AppError


class AdminService:
    """Logica de negocio para administradores. No conoce Flask ni HTTP.
    Solo llama al repository y lanza AppError si algo no cumple."""

    @staticmethod
    def list_all():
        """Listar todos los administradores."""
        return AdminRepository.get_all()

    @staticmethod
    def get_by_id(admin_id):
        """Obtener un admin por ID."""
        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)
        return admin

    @staticmethod
    def create(validated_data):
        """Crear un nuevo administrador.
        
        Args:
            validated_data: Dict con email, name, password
            
        Returns:
            Admin creado
            
        Raises:
            AppError: Si el email ya existe
        """
        email = validated_data['email']
        name = validated_data['name']
        password = validated_data['password']

        # Verificar que el email no exista
        if AdminRepository.get_by_email(email):
            raise AppError('El email ya esta registrado', 409)

        return AdminRepository.create(email, name, password)

    @staticmethod
    def update(admin_id, validated_data):
        """Actualizar datos de un administrador.
        
        Args:
            admin_id: ID del admin a actualizar
            validated_data: Dict con email y/o name
            
        Returns:
            Tupla (admin_actualizado, datos_anteriores) para auditoria
            
        Raises:
            AppError: Si el admin no existe o el email ya esta en uso
        """
        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        old_data = {
            'email': admin.email,
            'name': admin.name
        }

        new_email = validated_data.get('email')
        new_name = validated_data.get('name')

        # Si se proporciona un nuevo email, verificar que no este en uso
        if new_email and new_email != admin.email:
            existing = AdminRepository.get_by_email(new_email)
            if existing and existing.id != admin_id:
                raise AppError('El email ya esta en uso', 409)

        updated = AdminRepository.update(admin, email=new_email, name=new_name)
        return updated, old_data

    @staticmethod
    def change_password(admin_id, validated_data):
        """Cambiar contraseña de un administrador.
        
        Args:
            admin_id: ID del admin
            validated_data: Dict con password
            
        Returns:
            Admin actualizado
            
        Raises:
            AppError: Si el admin no existe
        """
        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        new_password = validated_data['password']
        return AdminRepository.update_password(admin, new_password)

    @staticmethod
    def toggle_status(admin_id, current_admin_id):
        """Activar/Desactivar un administrador.
        
        Args:
            admin_id: ID del admin a cambiar
            current_admin_id: ID del admin que ejecuta la accion
            
        Returns:
            Tupla (admin_actualizado, accion_realizada) para auditoria
            
        Raises:
            AppError: Si el admin no existe o intenta desactivarse a si mismo
        """
        # Validar que no intente desactivarse a si mismo
        if admin_id == current_admin_id:
            raise AppError('No puedes desactivar tu propia cuenta', 400)

        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        old_status = admin.is_active
        updated = AdminRepository.toggle_active(admin)
        
        action = 'ACTIVATE_ADMIN' if updated.is_active else 'DEACTIVATE_ADMIN'
        return updated, action, old_status