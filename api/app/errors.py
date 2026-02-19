from flask import jsonify
from .utils.responses import build_error_response

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        details = error.description if isinstance(error.description, dict) else str(error)
        return jsonify(build_error_response("ValidationError", "Bad Request", details)), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify(build_error_response("NotFound", "Resource not found", str(error))), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify(build_error_response("InternalServerError", "An unexpected error occurred", str(error))), 500
