#!/usr/bin/env python3
"""
Crea el primer admin del sistema.
Ejecutar desde la raiz del repo:

    python create_first_admin.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.database import db
from app.models import Admin


def main():
    app = create_app()
    with app.app_context():
        if Admin.query.first():
            print("Ya existe al menos un admin.")
            print("Usa POST /api/auth/admins para crear mas.")
            return

        print("No hay admins. Creando el primero...")
        email    = input("Email: ").strip()
        name     = input("Nombre: ").strip()
        password = input("Password: ").strip()

        if not all([email, name, password]):
            print("Todos los campos son requeridos. Abortando.")
            return

        admin = Admin(email=email, name=name)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin creado: {email}")


if __name__ == '__main__':
    main()