from flask import request
from ..database import db
from ..models import AuditLog


def log_audit(admin_id, action, entity=None, entity_id=None, details=None):
    """Registra una entrada en la bitacora. Se llama desde las rutas despues de cada operacion exitosa."""
    entry = AuditLog(
        admin_id=admin_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(entry)
    db.session.commit()