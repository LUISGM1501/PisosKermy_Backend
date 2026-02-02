from ..repositories.site_content_repository import SiteContentRepository
from ..utils.errors import AppError


class SiteContentService:

    @staticmethod
    def get_by_key(key):
        content = SiteContentRepository.get_by_key(key)
        if not content:
            raise AppError('Contenido no encontrado', 404)
        return content

    @staticmethod
    def get_or_create(key):
        """Obtiene el contenido con esa clave. Si no existe, lo crea vacio."""
        return SiteContentRepository.get_or_create(key)

    @staticmethod
    def update(key, validated_data, admin_id):
        content = SiteContentRepository.get_or_create(key)
        old_data = {
            'title':   content.title,
            'content': content.content,
        }
        updated = SiteContentRepository.update(content, validated_data, admin_id)
        return updated, old_data