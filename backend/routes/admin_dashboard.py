from flask import Blueprint, jsonify

from ..mysql_cli import scalar
from ..services import top_borrowed_books
from .helpers import require_api_role


admin_dashboard_bp = Blueprint("admin_dashboard_api", __name__, url_prefix="/api/admin")


@admin_dashboard_bp.route("/dashboard")
@require_api_role("librarian")
def api_admin_dashboard(user):
    stats = {
        key: scalar(sql, 0)
        for key, sql in {
            "books": "SELECT COUNT(*) c FROM book",
            "copies": "SELECT COUNT(*) c FROM book_copy",
            "borrowed": "SELECT COUNT(*) c FROM borrow_record WHERE status IN ('borrowed','overdue')",
            "reservations": "SELECT COUNT(*) c FROM reservation WHERE status IN ('waiting','notified')",
        }.items()
    }
    return jsonify({"ok": True, "stats": stats, "top_books": top_borrowed_books()})
