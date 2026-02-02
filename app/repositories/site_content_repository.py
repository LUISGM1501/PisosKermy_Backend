from ..database import db
from ..models import SiteContent


class SiteContentRepository:

    @staticmethod
    def get_by_key(key):
        return SiteContent.query.filter_by(key=key).first()

    @staticmethod
    def get_or_create(key):
        """Retorna el contenido con esa clave. Si no existe, lo crea vacio."""
        content = SiteContent.query.filter_by(key=key).first()
        if not content:
            content = SiteContent(key=key, title='', content='')
            db.session.add(content)
            db.session.commit()
        return content

    @staticmethod
    def update(site_content, data, admin_id):
        if 'title' in data:
            site_content.title = data['title']
        if 'content' in data:
            site_content.content = data['content']
        site_content.updated_by = admin_id
        db.session.commit()
        return site_content