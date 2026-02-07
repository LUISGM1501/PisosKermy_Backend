from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .database import db
from .utils.errors import register_error_handlers
from .utils.file import init_cloudinary


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar Cloudinary
    with app.app_context():
        init_cloudinary()

    # CORS configurado para permitir localhost:5173 y tu dominio de producción
    allowed_origins = app.config.get('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type"],
            "supports_credentials": True
        }
    })
    
    db.init_app(app)
    register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: importar para que SQLAlchemy registre los modelos
        db.create_all()

    # Blueprints
    from .routes.auth_routes         import auth_bp
    from .routes.admin_routes        import admin_bp  # NUEVO
    from .routes.category_routes     import category_bp
    from .routes.tag_routes          import tag_bp
    from .routes.provider_routes     import provider_bp
    from .routes.product_routes      import product_bp
    from .routes.site_content_routes import site_content_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)  # NUEVO
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(site_content_bp)

    # Endpoints genericos
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    # Ya no necesitamos servir uploads porque Cloudinary lo hace

    return app