from ..repositories.tag_repository import TagRepository
from ..utils.errors import AppError


class TagService:
    @staticmethod
    def list_all():
        return TagRepository.get_all()

    @staticmethod
    def get_by_id(tag_id):
        tag = TagRepository.get_by_id(tag_id)
        if not tag:
            raise AppError('Etiqueta no encontrada', 404)
        return tag

    @staticmethod
    def create(validated_data):
        name = validated_data['name']

        if TagRepository.get_by_name(name):
            raise AppError('Ya existe una etiqueta con ese nombre', 409)

        return TagRepository.create(name)

    @staticmethod
    def update(tag_id, validated_data):
        tag = TagRepository.get_by_id(tag_id)
        if not tag:
            raise AppError('Etiqueta no encontrada', 404)

        new_name = validated_data['name']

        existing = TagRepository.get_by_name(new_name)
        if existing and existing.id != tag_id:
            raise AppError('Ya existe una etiqueta con ese nombre', 409)

        old_name = tag.name
        updated = TagRepository.update(tag, new_name)
        return updated, old_name

    @staticmethod
    def delete(tag_id):
        tag = TagRepository.get_by_id(tag_id)
        if not tag:
            raise AppError('Etiqueta no encontrada', 404)

        deleted_name = tag.name
        TagRepository.delete(tag)
        return deleted_name