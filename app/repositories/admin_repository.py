from ..database import db
from ..models import Admin


class AdminRepository:
    """Unica capa que toca la base de datos para el modelo Admin.
    Los servicios nunca importan db ni hacen queries directamente."""

    @staticmethod
    def get_all():
        """Obtener todos los admins ordenados por fecha de creacion (mas recientes primero)."""
        return Admin.query.order_by(Admin.created_at.desc()).all()

    @staticmethod
    def get_by_id(admin_id):
        """Obtener admin por ID."""
        return db.session.get(Admin, admin_id)

    @staticmethod
    def get_by_email(email):
        """Obtener admin por email."""
        return Admin.query.filter_by(email=email).first()

    @staticmethod
    def create(email, name, password):
        """Crear un nuevo admin."""
        admin = Admin(email=email, name=name)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        return admin

    @staticmethod
    def update(admin, email=None, name=None):
        """Actualizar datos de un admin."""
        if email is not None:
            admin.email = email
        if name is not None:
            admin.name = name
        db.session.commit()
        return admin

    @staticmethod
    def update_password(admin, password):
        """Actualizar contraseña de un admin."""
        admin.set_password(password)
        db.session.commit()
        return admin

    @staticmethod
    def toggle_active(admin):
        """Cambiar estado activo/inactivo de un admin."""
        admin.is_active = not admin.is_active
        db.session.commit()
        return admin

    @staticmethod
    def count_active():
        """Contar admins activos."""
        return Admin.query.filter_by(is_active=True).count()