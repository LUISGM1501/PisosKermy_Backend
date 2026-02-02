from flask import Blueprint, request, jsonify
from ..models import Admin
from ..utils.auth import generate_token, require_auth
from ..utils.audit import log_audit

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400

    email    = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y password requeridos'}), 400

    admin = Admin.query.filter_by(email=email).first()

    if not admin or not admin.is_active or not admin.check_password(password):
        return jsonify({'error': 'Credenciales incorrectas'}), 401

    token = generate_token(admin.id)
    log_audit(admin.id, 'LOGIN')

    return jsonify({
        'token': token,
        'admin': {
            'id':    admin.id,
            'email': admin.email,
            'name':  admin.name,
        }
    })


@auth_bp.route('/api/auth/me', methods=['GET'])
@require_auth
def get_me():
    admin = request.current_admin
    return jsonify({
        'id':        admin.id,
        'email':     admin.email,
        'name':      admin.name,
        'is_active': admin.is_active,
    })

# ---------------------------------------------------------------------------
# Bitacora (solo lectura, solo admins)
# ---------------------------------------------------------------------------

@auth_bp.route('/api/auth/audit', methods=['GET'])
@require_auth
def list_audit_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    from ..models import AuditLog

    paginated = (
        AuditLog.query
        .order_by(AuditLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    logs = []
    for log in paginated.items:
        logs.append({
            'id': log.id,
            'admin_id': log.admin_id,
            'admin_email': log.admin.email if log.admin else None,
            'action': log.action,
            'entity': log.entity,
            'entity_id': log.entity_id,
            'details': log.details,
            'ip_address': log.ip_address,
            'created_at': log.created_at.isoformat() if log.created_at else None,
        })

    return jsonify({
        'logs': logs,
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
    })