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
        """Crear un nuevo administrador."""
        email = validated_data['email']
        name = validated_data['name']
        password = validated_data['password']

        if AdminRepository.get_by_email(email):
            raise AppError('El email ya esta registrado', 409)

        return AdminRepository.create(email, name, password)

    @staticmethod
    def update(admin_id, validated_data, current_admin_id):
        """Actualizar datos de un administrador.
        
        PROTECCION: Solo el admin 1 puede modificar al admin 1
        """
        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        # PROTECCION: Solo admin 1 puede modificar admin 1
        if admin_id == 1 and current_admin_id != 1:
            raise AppError('No tienes permisos para modificar al administrador principal', 403)

        old_data = {
            'email': admin.email,
            'name': admin.name
        }

        new_email = validated_data.get('email')
        new_name = validated_data.get('name')

        if new_email and new_email != admin.email:
            existing = AdminRepository.get_by_email(new_email)
            if existing and existing.id != admin_id:
                raise AppError('El email ya esta en uso', 409)

        updated = AdminRepository.update(admin, email=new_email, name=new_name)
        return updated, old_data

    @staticmethod
    def change_password(admin_id, validated_data, current_admin_id):
        """Cambiar contraseña de un administrador.
        
        PROTECCION: Solo el admin 1 puede cambiar password del admin 1
        """
        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        # PROTECCION: Solo admin 1 puede cambiar password de admin 1
        if admin_id == 1 and current_admin_id != 1:
            raise AppError('No tienes permisos para cambiar la contraseña del administrador principal', 403)

        new_password = validated_data['password']
        return AdminRepository.update_password(admin, new_password)

    @staticmethod
    def toggle_status(admin_id, current_admin_id):
        """Activar/Desactivar un administrador.
        
        PROTECCIONES:
        - No puede desactivarse a si mismo
        - NO se puede desactivar al admin 1 (nunca)
        """
        # No puede desactivarse a si mismo
        if admin_id == current_admin_id:
            raise AppError('No puedes desactivar tu propia cuenta', 400)

        # PROTECCION: NADIE puede desactivar al admin 1
        if admin_id == 1:
            raise AppError('No se puede desactivar al administrador principal', 403)

        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        old_status = admin.is_active
        updated = AdminRepository.toggle_active(admin)
        
        action = 'ACTIVATE_ADMIN' if updated.is_active else 'DEACTIVATE_ADMIN'
        return updated, action, old_status

    @staticmethod
    def delete(admin_id, current_admin_id):
        """Eliminar un administrador permanentemente.
        
        PROTECCIONES:
        - No puede eliminarse a si mismo
        - NO se puede eliminar al admin 1 (nunca)
        """
        # No puede eliminarse a si mismo
        if admin_id == current_admin_id:
            raise AppError('No puedes eliminar tu propia cuenta', 400)

        # PROTECCION: NADIE puede eliminar al admin 1
        if admin_id == 1:
            raise AppError('No se puede eliminar al administrador principal', 403)

        admin = AdminRepository.get_by_id(admin_id)
        if not admin:
            raise AppError('Admin no encontrado', 404)

        email = admin.email
        name = admin.name
        
        AdminRepository.delete(admin)
        
        return email, name