from flask import Blueprint, jsonify, request

from ..audit import log_event
from ..mysql_cli import mysql, q, scalar
from .helpers import api_error, payload, require_api_role


admin_circulation_bp = Blueprint("admin_circulation_api", __name__, url_prefix="/api/admin")


@admin_circulation_bp.route("/borrow", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_borrow(user):
    if request.method == "POST":
        form = payload()
        student_no = scalar(f"SELECT student_no FROM student WHERE LOWER(student_id)=LOWER({q(form.get('student_id'))})")
        copy_no = scalar(f"SELECT copy_no FROM book_copy WHERE barcode={q(form.get('barcode'))}")
        if not student_no or not copy_no:
            return api_error("学号或条码不存在")
        mysql(f"CALL sp_borrow_book({student_no},{copy_no},{user['no']})")
        log_event("book_borrowed", user, student_no=student_no, copy_no=copy_no)
        return jsonify({"ok": True, "message": "借书成功"})
    rows = mysql(
        "SELECT bc.barcode,b.title,bc.location,bc.status "
        "FROM book_copy bc JOIN book b ON b.book_no=bc.book_no ORDER BY bc.status,b.title",
        True,
    )
    return jsonify({"ok": True, "rows": rows})


@admin_circulation_bp.route("/return", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_return(user):
    if request.method == "POST":
        borrow_no = payload().get("borrow_no")
        mysql(f"CALL sp_return_book({q(borrow_no)},{user['no']})")
        log_event("book_returned", user, borrow_no=borrow_no)
        return jsonify({"ok": True, "message": "还书成功"})
    rows = mysql(
        "SELECT br.borrow_no,s.student_id,s.name,b.title,bc.barcode,br.borrow_time,br.due_time,br.status "
        "FROM borrow_record br "
        "JOIN student s ON s.student_no=br.student_no "
        "JOIN book_copy bc ON bc.copy_no=br.copy_no "
        "JOIN book b ON b.book_no=bc.book_no "
        "WHERE br.status IN ('borrowed','overdue') ORDER BY br.due_time",
        True,
    )
    return jsonify({"ok": True, "rows": rows})


@admin_circulation_bp.route("/reservations", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_reservations(user):
    if request.method == "POST":
        form = payload()
        mysql(
            "UPDATE reservation "
            f"SET status={q(form.get('status'))}, handled_by_no={user['no']}, handled_at=NOW() "
            f"WHERE reservation_no={q(form.get('reservation_no'))}"
        )
        log_event("reservation_updated", user, reservation_no=form.get("reservation_no"), status=form.get("status"))
        return jsonify({"ok": True, "message": "预约状态已更新"})
    rows = mysql(
        "SELECT r.reservation_no,s.student_id,s.name,b.title,r.reserved_at,r.borrow_date,r.expire_at,r.status "
        "FROM reservation r "
        "JOIN student s ON s.student_no=r.student_no "
        "JOIN book b ON b.book_no=r.book_no "
        "ORDER BY r.reservation_no DESC",
        True,
    )
    return jsonify({"ok": True, "rows": rows})


@admin_circulation_bp.route("/overdue", methods=["GET", "POST"])
@require_api_role("librarian")
def api_admin_overdue(user):
    if request.method == "POST":
        overdue_no = payload().get("overdue_no")
        mysql(f"UPDATE overdue_record SET paid_amount=fine_amount,status='paid',paid_at=NOW() WHERE overdue_no={q(overdue_no)}")
        log_event("overdue_paid", user, overdue_no=overdue_no)
        return jsonify({"ok": True, "message": "罚金已登记缴清"})
    rows = mysql(
        "SELECT o.overdue_no,s.student_id,s.name,b.title,o.overdue_days,o.fine_amount,o.paid_amount,o.status "
        "FROM overdue_record o "
        "JOIN borrow_record br ON br.borrow_no=o.borrow_no "
        "JOIN student s ON s.student_no=br.student_no "
        "JOIN book_copy bc ON bc.copy_no=br.copy_no "
        "JOIN book b ON b.book_no=bc.book_no "
        "ORDER BY o.overdue_no DESC",
        True,
    )
    return jsonify({"ok": True, "rows": rows})
