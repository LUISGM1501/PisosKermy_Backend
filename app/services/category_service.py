from ..repositories.category_repository import CategoryRepository
from ..utils.errors import AppError


class CategoryService:
    """Logica de negocio para categorias. No conoce Flask ni HTTP.
    Solo llama al repository y lanza AppError si algo no cumple."""

    @staticmethod
    def list_all():
        return CategoryRepository.get_all()

    @staticmethod
    def get_by_id(category_id):
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise AppError('Categoria no encontrada', 404)
        return category

    @staticmethod
    def create(validated_data):
        name = validated_data['name']

        if CategoryRepository.get_by_name(name):
            raise AppError('Ya existe una categoria con ese nombre', 409)

        return CategoryRepository.create(name)

    @staticmethod
    def update(category_id, validated_data):
        """Retorna (categoria_actualizada, nombre_anterior) para que la ruta pueda loguear la bitacora."""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise AppError('Categoria no encontrada', 404)

        new_name = validated_data['name']

        existing = CategoryRepository.get_by_name(new_name)
        if existing and existing.id != category_id:
            raise AppError('Ya existe una categoria con ese nombre', 409)

        old_name = category.name
        updated = CategoryRepository.update(category, new_name)
        return updated, old_name

    @staticmethod
    def delete(category_id):
        """Retorna el nombre de la categoria eliminada para la bitacora."""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise AppError('Categoria no encontrada', 404)

        deleted_name = category.name
        CategoryRepository.delete(category)
        return deleted_name