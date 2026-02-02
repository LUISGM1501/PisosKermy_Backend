from flask import Blueprint, request, jsonify
from ..services.site_content_service import SiteContentService
from ..schemas.site_content import SiteContentUpdateSchema, SiteContentResponseSchema
from ..utils.auth import require_auth
from ..utils.audit import log_audit
from ..utils.errors import ValidationError

site_content_bp = Blueprint('site_content', __name__)


# ---------------------------------------------------------------------------
# Publico — el cliente puede leer el contenido del sitio
# ---------------------------------------------------------------------------

@site_content_bp.route('/api/site-content/<key>', methods=['GET'])
def get_site_content(key):
    """Retorna el contenido con esa clave. Si no existe, retorna vacio."""
    content = SiteContentService.get_or_create(key)
    return jsonify(SiteContentResponseSchema.serialize(content))


# ---------------------------------------------------------------------------
# Admin — editar contenido del sitio
# ---------------------------------------------------------------------------

@site_content_bp.route('/api/admin/site-content/<key>', methods=['PUT'])
@require_auth
def update_site_content(key):
    validated, errors = SiteContentUpdateSchema.validate(request.get_json())
    if errors:
        raise ValidationError(errors)

    content, old_data = SiteContentService.update(key, validated, request.current_admin.id)

    log_audit(
        admin_id=request.current_admin.id,
        action='UPDATE',
        entity='site_content',
        entity_id=content.id,
        details={'key': key, 'old': old_data, 'new': SiteContentResponseSchema.serialize(content)}
    )

    return jsonify(SiteContentResponseSchema.serialize(content))