class SiteContentUpdateSchema:
    @staticmethod
    def validate(data):
        if not data or not isinstance(data, dict):
            return None, {'general': 'Se requiere un objeto JSON'}

        errors  = {}
        cleaned = {}

        if 'title' in data:
            title = data['title']
            if title is not None and len(str(title).strip()) > 200:
                errors['title'] = 'El titulo no puede superar 200 caracteres'
            else:
                cleaned['title'] = str(title).strip() if title else None

        if 'content' in data:
            cleaned['content'] = str(data['content']).strip() if data['content'] else None

        if errors:
            return None, errors

        if not cleaned:
            return None, {'general': 'No hay campos para actualizar'}

        return cleaned, None


class SiteContentResponseSchema:
    @staticmethod
    def serialize(site_content):
        return {
            'id':         site_content.id,
            'key':        site_content.key,
            'title':      site_content.title,
            'content':    site_content.content,
            'updated_at': site_content.updated_at.isoformat() if site_content.updated_at else None,
            'updated_by': site_content.updated_by,
        }

    @staticmethod
    def serialize_many(site_contents):
        return [SiteContentResponseSchema.serialize(sc) for sc in site_contents]