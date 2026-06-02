from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from .config import HOST, PORT, SECRET_KEY, SESSION_COOKIE
from .logging_config import RUNTIME_LOGGER
from .routes import register_blueprints
from .services import ensure_demo_accounts


def create_app():
    ensure_demo_accounts()
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config.update(HOST=HOST, PORT=PORT, SESSION_COOKIE_NAME=SESSION_COOKIE)
    register_error_handlers(app)
    register_blueprints(app)
    RUNTIME_LOGGER.info("app_created host=%s port=%s", HOST, PORT)
    return app


def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(exc):
        if isinstance(exc, HTTPException):
            return jsonify({"ok": False, "message": exc.description}), exc.code
        RUNTIME_LOGGER.exception("request_failed")
        return jsonify({"ok": False, "message": "服务器内部错误"}), 500
