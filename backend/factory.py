from flask import Flask, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException

from .config import HOST, MAX_UPLOAD_SIZE, PORT, SECRET_KEY, SESSION_COOKIE, UPLOAD_DIR
from .logging_config import RUNTIME_LOGGER
from .routes import register_blueprints
from .services import ensure_demo_accounts
from flask import request


def create_app():
    ensure_demo_accounts()
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config.update(HOST=HOST, PORT=PORT, SESSION_COOKIE_NAME=SESSION_COOKIE, MAX_CONTENT_LENGTH=MAX_UPLOAD_SIZE)
    register_error_handlers(app)
    register_blueprints(app)
    # Allow CORS for development frontend on different port
    @app.before_request
    def handle_options():
        if request.method == 'OPTIONS':
            return app.make_default_options_response()

    @app.after_request
    def add_cors(response):
        origin = request.headers.get('Origin')
        if origin and origin.startswith('http://127.0.0.1'):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response
    # Serve uploaded files from the uploads directory
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(str(UPLOAD_DIR), filename)
    RUNTIME_LOGGER.info("app_created host=%s port=%s", HOST, PORT)
    return app


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(exc):
        if isinstance(exc, HTTPException):
            return jsonify({"ok": False, "message": exc.description}), exc.code
        RUNTIME_LOGGER.exception("request_failed")
        return jsonify({"ok": False, "message": "服务器内部错误"}), 500
