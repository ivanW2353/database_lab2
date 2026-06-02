from .admin_books import admin_books_bp
from .admin_circulation import admin_circulation_bp
from .admin_dashboard import admin_dashboard_bp
from .admin_users import admin_users_bp
from .auth import auth_api_bp
from .student import student_api_bp


def register_blueprints(app):
    app.register_blueprint(auth_api_bp)
    app.register_blueprint(student_api_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_books_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_circulation_bp)
