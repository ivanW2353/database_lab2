from flask import Blueprint, jsonify, session
from datetime import date

from ..audit import log_event
from ..mysql_cli import mysql, q, scalar
from ..security import PASSWORD_POLICY_MESSAGE, hash_password, validate_password, verify_password
from ..services import PLACEHOLDER_STUDENT_NAME, book_categories, book_detail, book_rows, top_borrowed_books
from ..validators import validate_email, validate_phone
from .helpers import api_error, db_api_error, payload, require_api_role


student_api_bp = Blueprint("student_api", __name__, url_prefix="/api")


@student_api_bp.route("/books")
def api_books():
    from flask import request
    return jsonify({
        "ok": True,
        "books": book_rows(
            request.args.get("q", ""),
            request.args.get("category_no", ""),
            request.args.get("category_code", ""),
        ),
        "categories": book_categories(),
    })


@student_api_bp.route("/books/<int:book_no>")
def api_book_detail(book_no):
    detail = book_detail(book_no)
    if not detail:
        return api_error("图书不存在", 404)
    return jsonify({"ok": True, "book": detail})


@student_api_bp.route("/student/dashboard")
@require_api_role("student")
def api_student_dashboard(user):
    stats = {
        "borrow": scalar(f"SELECT COUNT(*) c FROM borrow_record WHERE student_no={user['no']} AND status IN ('borrowed','overdue')", 0),
        "reserve": scalar(f"SELECT COUNT(*) c FROM reservation WHERE student_no={user['no']} AND status IN ('waiting','notified')", 0),
        "fine": scalar(f"SELECT COALESCE(SUM(o.fine_amount-o.paid_amount),0) c FROM overdue_record o JOIN borrow_record b ON b.borrow_no=o.borrow_no WHERE b.student_no={user['no']} AND o.status IN ('unpaid','partial_paid')", "0.00"),
    }
    return jsonify({"ok": True, "stats": stats, "top_books": top_borrowed_books()})


@student_api_bp.route("/student/borrows", methods=["GET", "POST"])
@require_api_role("student")
def api_student_borrows(user):
    from flask import request
    if request.method == "POST":
        data = payload()
        book_no = data.get("book_no")
        if not scalar(f"SELECT book_no FROM book WHERE book_no={q(book_no)}"):
            return api_error("图书不存在")
        copy_no = scalar(
            "SELECT copy_no FROM book_copy "
            f"WHERE book_no={q(book_no)} AND status='available' ORDER BY copy_no LIMIT 1"
        )
        if not copy_no:
            try:
                mysql(
                    "INSERT INTO reservation (student_no, book_no, expire_at) "
                    f"VALUES ({user['no']},{q(book_no)},DATE_ADD(NOW(), INTERVAL 3 DAY))"
                )
            except RuntimeError as exc:
                log_event("book_waitlist_failed", user, book_no=book_no, error=exc)
                return db_api_error(exc)
            log_event("book_waitlist_joined", user, book_no=book_no)
            return jsonify({"ok": True, "message": "当前无可借馆藏，已为你加入预约队列"})
        try:
            mysql(f"CALL sp_borrow_book({q(user['no'])},{q(copy_no)},NULL)")
        except RuntimeError as exc:
            log_event("book_self_borrow_failed", user, book_no=book_no, copy_no=copy_no, error=exc)
            return db_api_error(exc)
        log_event("book_self_borrowed", user, book_no=book_no, copy_no=copy_no)
        return jsonify({"ok": True, "message": "借出成功，请按期归还"})
    rows = mysql(f"SELECT br.borrow_no,b.title,bc.barcode,br.borrow_time,br.due_time,br.return_time,br.status FROM borrow_record br JOIN book_copy bc ON bc.copy_no=br.copy_no JOIN book b ON b.book_no=bc.book_no WHERE br.student_no={user['no']} ORDER BY br.borrow_no DESC", True)
    return jsonify({"ok": True, "rows": rows})


@student_api_bp.route("/student/reservations", methods=["GET", "POST", "DELETE"])
@require_api_role("student")
def api_student_reservations(user):
    from flask import request
    if request.method == "DELETE":
        data = payload()
        reservation_no = data.get("reservation_no")
        rows = mysql(
            "SELECT reservation_no,status FROM reservation "
            f"WHERE reservation_no={q(reservation_no)} AND student_no={q(user['no'])}",
            True,
        )
        if not rows:
            return api_error("预约记录不存在")
        if rows[0]["status"] not in ("waiting", "notified"):
            return api_error("该预约当前状态不能取消")
        mysql(
            "UPDATE reservation SET status='cancelled' "
            f"WHERE reservation_no={q(reservation_no)} AND student_no={q(user['no'])}"
        )
        log_event("reservation_cancelled", user, reservation_no=reservation_no)
        return jsonify({"ok": True, "message": "预约已取消"})

    if request.method == "POST":
        data = payload()
        book_no = data.get("book_no")
        if not scalar(f"SELECT book_no FROM book WHERE book_no={q(book_no)}"):
            return api_error("图书不存在")
        borrow_date = (data.get("borrow_date") or "").strip()
        if not borrow_date:
            return api_error("请选择预约借出日期")
        try:
            selected_date = date.fromisoformat(borrow_date)
        except ValueError:
            return api_error("预约借出日期格式不正确")
        if selected_date <= date.today():
            return api_error("预约借出日期必须晚于今天")
        try:
            mysql(
                "INSERT INTO reservation (student_no, book_no, borrow_date, expire_at) "
                f"VALUES ({user['no']},{q(book_no)},{q(borrow_date)},DATE_ADD({q(borrow_date)}, INTERVAL 1 DAY))"
            )
        except RuntimeError as exc:
            log_event("reservation_create_failed", user, book_no=book_no, borrow_date=borrow_date, error=exc)
            return db_api_error(exc)
        log_event("reservation_created", user, book_no=book_no, borrow_date=borrow_date)
        return jsonify({"ok": True, "message": "预约已提交"})
    rows = mysql(f"SELECT r.reservation_no,b.title,r.reserved_at,r.borrow_date,r.expire_at,r.status FROM reservation r JOIN book b ON b.book_no=r.book_no WHERE r.student_no={user['no']} ORDER BY r.reservation_no DESC", True)
    return jsonify({"ok": True, "rows": rows})


@student_api_bp.route("/student/overdue")
@require_api_role("student")
def api_student_overdue(user):
    rows = mysql(f"SELECT o.overdue_no,b.title,o.overdue_days,o.fine_amount,o.paid_amount,o.status FROM overdue_record o JOIN borrow_record br ON br.borrow_no=o.borrow_no JOIN book_copy bc ON bc.copy_no=br.copy_no JOIN book b ON b.book_no=bc.book_no WHERE br.student_no={user['no']} ORDER BY o.overdue_no DESC", True)
    return jsonify({"ok": True, "rows": rows})


@student_api_bp.route("/student/profile", methods=["GET", "POST"])
@require_api_role("student")
def api_student_profile(user):
    from flask import request
    if request.method == "POST":
        data = payload()
        current_name = scalar(f"SELECT name FROM student WHERE student_no={q(user['no'])}", "")
        name_sql = ""
        submitted_name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        email = (data.get("email") or "").strip()
        if current_name == PLACEHOLDER_STUDENT_NAME and not submitted_name:
            return api_error("首次完善个人信息时必须填写姓名")
        if not phone and not email:
            return api_error("电话和邮箱至少填写一项")
        if not validate_phone(phone):
            return api_error("电话格式不正确，请填写 11 位手机号或座机号")
        if not validate_email(email):
            return api_error("邮箱格式不正确")
        if current_name == PLACEHOLDER_STUDENT_NAME and submitted_name:
            name_sql = f"name={q(submitted_name)}, "
            session["user"] = {**user, "name": submitted_name}
        mysql(
            "UPDATE student SET "
            f"{name_sql}gender={q(data.get('gender') or 'other')}, college={q(data.get('college'))}, "
            f"major={q(data.get('major'))}, phone={q(phone)}, email={q(email)} "
            f"WHERE student_no={q(user['no'])}"
        )
        log_event("student_profile_updated", user)
        return jsonify({"ok": True, "message": "个人信息已保存", "user": session.get("user", user)})
    rows = mysql(f"SELECT student_id,name,gender,college,major,phone,email,student_type,status FROM student WHERE student_no={q(user['no'])}", True)
    return jsonify({"ok": True, "student": rows[0] if rows else {}})


@student_api_bp.route("/student/password", methods=["POST"])
@require_api_role("student")
def api_student_password(user):
    data = payload()
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    confirm_password = data.get("confirm_password", "")
    rows = mysql(f"SELECT password_hash FROM student WHERE student_no={q(user['no'])}", True)
    if not rows or not verify_password(old_password, rows[0]["password_hash"]):
        log_event("student_password_change_failed", user, reason="bad_old_password")
        return api_error("原密码错误")
    if not validate_password(new_password):
        return api_error(PASSWORD_POLICY_MESSAGE)
    if new_password != confirm_password:
        return api_error("两次输入的新密码不一致")
    mysql(f"UPDATE student SET password_hash={q(hash_password(new_password))} WHERE student_no={q(user['no'])}")
    log_event("student_password_changed", user)
    return jsonify({"ok": True, "message": "密码已修改"})
