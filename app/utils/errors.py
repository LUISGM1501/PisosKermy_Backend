from flask import jsonify


class AppError(Exception):
    """Error de dominio. Cada servicio lo lanza cuando algo no cumple reglas de negocio."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(Exception):
    """Error de validacion de entrada. Contiene un diccionario de errores por campo."""
    def __init__(self, errors):
        super().__init__('Errores de validacion')
        self.errors = errors


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({'errors': error.errors}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso no encontrado'}), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({'error': 'Metodo no permitido'}), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor'}), 500