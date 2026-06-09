import mimetypes
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from ..audit import log_event
from ..logging_config import RUNTIME_LOGGER
from ..config import BASE_DIR, UPLOAD_DIR
from ..mysql_cli import mysql, q
from ..services import book_borrow_records, book_detail, book_rows
from .helpers import api_error, db_api_error, payload, require_api_role


admin_books_bp = Blueprint("admin_books_api", __name__, url_prefix="/api/admin")


@admin_books_bp.route("/books/<int:book_no>")
@require_api_role("librarian")
def api_admin_book_detail(user, book_no):
    detail = book_detail(book_no)
    if not detail:
        return api_error("图书不存在", 404)
    detail["borrow_records"] = book_borrow_records(book_no)
    return jsonify({"ok": True, "book": detail})


@admin_books_bp.route("/books", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_books(user):
    if request.method == "POST":
        form = payload()
        action = form.get("action")
        try:
            RUNTIME_LOGGER.info("api_admin_books_called user=%s action=%s form=%s", user and user.get('no'), action, {k: (v if k!='file' else '<file>') for k,v in form.items()})
        except Exception:
            RUNTIME_LOGGER.exception("api_admin_books_log_failed")
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
                f"COALESCE(NULLIF({q(form.get('purchase_date', ''))},''),CURDATE()))"
            )
            log_event("copy_created", user, barcode=form.get("barcode"))
        elif action == "summary":
            book_no = form.get("book_no")
            try:
                mysql(f"CALL sp_update_book_summary({q(book_no)},{q(form.get('summary', ''))})")
            except RuntimeError as exc:
                return db_api_error(exc)
            log_event("book_summary_updated", user, book_no=book_no)
            return jsonify({"ok": True, "message": "图书简介已修改"})
        elif action == "media":
            book_no = form.get("book_no")
            uploaded_file = request.files.get("file")
            if not book_no or not uploaded_file or not uploaded_file.filename:
                return api_error("请选择图书和本地文件")
            if not mysql(f"SELECT book_no FROM book WHERE book_no={q(book_no)}", True):
                return api_error("图书不存在")
            title = Path(uploaded_file.filename).name
            safe_name = secure_filename(title)
            suffix = Path(safe_name or title).suffix.lower()
            upload_dir = UPLOAD_DIR / "books" / str(book_no)
            upload_dir.mkdir(parents=True, exist_ok=True)
            saved_path = upload_dir / f"{uuid4().hex}{suffix}"
            file_path = saved_path.relative_to(BASE_DIR).as_posix()
            mime_type = mimetypes.guess_type(title)[0] or (uploaded_file.mimetype if uploaded_file and uploaded_file.mimetype else None) or "application/octet-stream"
            # Only accept image uploads
            if not mime_type or not mime_type.startswith("image/"):
                return api_error("仅允许上传图片")
            media_type = "image"
            try:
                try:
                    uploaded_file.save(saved_path)
                finally:
                    uploaded_file.close()
                file_size = saved_path.stat().st_size
                mysql(
                    "INSERT INTO book_media (book_no,media_type,title,file_path,mime_type,file_size,uploaded_by_no) "
                    f"VALUES ({q(book_no)},{q(media_type)},{q(title)},{q(file_path)},{q(mime_type)},{q(file_size)},{user['no']})"
                )
                # fetch the created media row to return to client for immediate display
                last = mysql("SELECT LAST_INSERT_ID() AS last", True)
                media_row = None
                if last:
                    media_id = last[0].get('last')
                    if media_id:
                        rows = mysql(f"SELECT media_no,book_no,media_type,title,file_path,mime_type,file_size,uploaded_by_no FROM book_media WHERE media_no={q(media_id)}", True)
                        if rows:
                            media_row = rows[0]
            except Exception:
                saved_path.unlink(missing_ok=True)
                raise
            log_event("media_created", user, title=title, file_path=file_path)
            if media_row:
                return jsonify({"ok": True, "message": "保存成功", "media": media_row})
        elif action == "delete_media":
            media_no = form.get("media_no")
            RUNTIME_LOGGER.info("delete_media_attempt user=%s media_no=%s", user and user.get('no'), media_no)
            if not media_no:
                return api_error("缺少 media_no")
            rows = mysql(f"SELECT file_path,title FROM book_media WHERE media_no={q(media_no)}", True)
            if not rows:
                RUNTIME_LOGGER.info("delete_media_not_found media_no=%s", media_no)
                return api_error("媒体文件不存在", 404)
            row = rows[0]
            try:
                file_on_disk = BASE_DIR / row["file_path"]
                try:
                    file_on_disk.unlink(missing_ok=True)
                except Exception as e:
                    RUNTIME_LOGGER.exception("delete_media_unlink_failed media_no=%s file=%s", media_no, file_on_disk)
                    # ignore file remove errors, still attempt DB delete
                    pass
                mysql(f"DELETE FROM book_media WHERE media_no={q(media_no)}")
            except Exception as exc:
                RUNTIME_LOGGER.exception("delete_media_failed media_no=%s", media_no)
                return db_api_error(exc)
            log_event("media_deleted", user, media_no=media_no, title=row.get("title"), file_path=row.get("file_path"))
            return jsonify({"ok": True, "message": "删除成功"})

    books, pagination = book_rows(keyword=request.args.get("keyword", ""),
                                  page=request.args.get("page", 1),
                                  page_size=request.args.get("page_size", 10))
    return jsonify({
        "ok": True,
        "books": books,
        "pagination": pagination,
        "book_options": mysql("SELECT book_no,title FROM book ORDER BY title,book_no", True),
        "categories": mysql("SELECT category_no,category_code,category_name FROM book_category ORDER BY category_code", True),
        "publishers": mysql("SELECT publisher_no,publisher_name FROM publisher ORDER BY publisher_no", True),
    })
