from flask import Blueprint, jsonify, request

from ..audit import log_event
from ..mysql_cli import mysql, q
from ..services import book_rows
from .helpers import payload, require_api_role


admin_books_bp = Blueprint("admin_books_api", __name__, url_prefix="/api/admin")


@admin_books_bp.route("/books", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_books(user):
    if request.method == "POST":
        form = payload()
        action = form.get("action")
        if action == "book":
            mysql(
                "INSERT INTO book "
                "(isbn,title,category_no,publisher_no,publish_date,edition,price,language,summary) "
                f"VALUES ({q(form.get('isbn'))},{q(form.get('title'))},{q(form.get('category_no'))},"
                f"{q(form.get('publisher_no') or None)},NULLIF({q(form.get('publish_date', ''))},''),"
                f"{q(form.get('edition'))},NULLIF({q(form.get('price', ''))},''),"
                f"{q(form.get('language') or 'Chinese')},{q(form.get('summary'))})"
            )
            log_event("book_created", user, title=form.get("title"))
        elif action == "copy":
            mysql(
                "INSERT INTO book_copy (book_no,barcode,location,purchase_date) "
                f"VALUES ({q(form.get('book_no'))},{q(form.get('barcode'))},{q(form.get('location'))},"
                f"NULLIF({q(form.get('purchase_date', ''))},''))"
            )
            log_event("copy_created", user, barcode=form.get("barcode"))
        elif action == "media":
            mysql(
                "INSERT INTO book_media (book_no,media_type,title,file_path,mime_type,uploaded_by_no) "
                f"VALUES ({q(form.get('book_no'))},{q(form.get('media_type'))},{q(form.get('title'))},"
                f"{q(form.get('file_path'))},{q(form.get('mime_type'))},{user['no']})"
            )
            log_event("media_created", user, title=form.get("title"))
        return jsonify({"ok": True, "message": "保存成功"})

    return jsonify({
        "ok": True,
        "books": book_rows(),
        "categories": mysql("SELECT category_no,category_code,category_name FROM book_category ORDER BY category_code", True),
        "publishers": mysql("SELECT publisher_no,publisher_name FROM publisher ORDER BY publisher_no", True),
    })
