from ..database import db
from ..models import Category


class CategoryRepository:
    """Unica capa que toca la base de datos para el modelo Category.
    Los servicios nunca importan db ni hacen queries directamente."""

    @staticmethod
    def get_all():
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def get_by_name(name):
        return Category.query.filter_by(name=name).first()

    @staticmethod
    def create(name):
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def update(category, name):
        category.name = name
        db.session.commit()
        return category

    @staticmethod
    def delete(category):
        db.session.delete(category)
        db.session.commit()