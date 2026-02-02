from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from .config import Config
from .database import db
from .utils.errors import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    register_error_handlers(app)

    with app.app_context():
        from . import models  # noqa: importar para que SQLAlchemy registre los modelos
        db.create_all()

    # Blueprints
    from .routes.auth_routes         import auth_bp
    from .routes.category_routes     import category_bp
    from .routes.tag_routes          import tag_bp
    from .routes.provider_routes     import provider_bp
    from .routes.product_routes      import product_bp
    from .routes.site_content_routes import site_content_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(tag_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(site_content_bp)

    # Endpoints genericos
    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app