from flask import Blueprint, jsonify, request

from ..audit import log_event
from ..mysql_cli import mysql, q, scalar
from ..pagination import paginate
from ..services import DEFAULT_LIBRARIAN_PASSWORD, DEFAULT_STUDENT_PASSWORD, create_librarian, create_student_with_id
from .helpers import api_error, payload, require_api_role


admin_users_bp = Blueprint("admin_users_api", __name__, url_prefix="/api/admin")


@admin_users_bp.route("/students/<student_id>")
@require_api_role("librarian")
def api_admin_student_detail(user, student_id):
    rows = mysql(
        "SELECT student_id,name,gender,college,major,phone,email,student_type,status,created_at "
        f"FROM student WHERE student_id={q(student_id)}",
        True,
    )
    if not rows:
        return api_error("学生不存在", 404)
    student = rows[0]
    student["borrow_records"] = mysql(
        "SELECT br.borrow_no,br.borrow_code,b.title,bc.barcode,br.borrow_time,br.due_time,"
        "br.return_time,br.renew_count,br.status "
        "FROM borrow_record br "
        "JOIN student s ON s.student_no=br.student_no "
        "JOIN book_copy bc ON bc.copy_no=br.copy_no "
        "JOIN book b ON b.book_no=bc.book_no "
        f"WHERE s.student_id={q(student_id)} ORDER BY br.borrow_no DESC",
        True,
    )
    return jsonify({"ok": True, "student": student})


@admin_users_bp.route("/students", methods=["GET", "POST", "DELETE"])
@require_api_role("librarian")
def api_admin_students(user):
    if request.method == "POST":
        form = payload()
        try:
            student_id = create_student_with_id(form.get("student_id"))
        except ValueError as exc:
            return api_error(str(exc))
        log_event("student_created", user, student_id=student_id)
        return jsonify({"ok": True, "message": f"学生已添加，初始密码为 {DEFAULT_STUDENT_PASSWORD}"})

    if request.method == "DELETE":
        form = payload()
        student_id = (form.get("student_id") or "").strip()
        student_no = scalar(f"SELECT student_no FROM student WHERE LOWER(student_id)=LOWER({q(student_id)})")
        if not student_no:
            return api_error("学生不存在")
        related = int(scalar(
            "SELECT "
            f"(SELECT COUNT(*) FROM borrow_record WHERE student_no={q(student_no)}) + "
            f"(SELECT COUNT(*) FROM reservation WHERE student_no={q(student_no)}) c",
            0,
        ))
        if related:
            return api_error("该学生已有借阅或预约记录，不能直接删除")
        mysql(f"DELETE FROM student WHERE student_no={q(student_no)}")
        log_event("student_deleted", user, student_id=student_id)
        return jsonify({"ok": True, "message": "学生已删除"})

    student_id = (request.args.get("student_id") or "").strip()
    name = (request.args.get("name") or "").strip()
    where = []
    if student_id:
        where.append(f"student_id LIKE {q('%' + student_id + '%')}")
    if name:
        where.append(f"name LIKE {q('%' + name + '%')}")
    where_sql = " WHERE " + " AND ".join(where) if where else ""
    rows, pagination = paginate(
        "SELECT student_id,name,college,major,student_type,status "
        f"FROM student{where_sql} ORDER BY student_id",
        f"SELECT COUNT(*) c FROM student{where_sql}",
    )
    return jsonify({"ok": True, "rows": rows, "pagination": pagination})


@admin_users_bp.route("/librarians", methods=["GET", "POST", "DELETE"])
@require_api_role("librarian")
def api_admin_librarians(user):
    if request.method == "POST":
        form = payload()
        try:
            employee_id = create_librarian(
                form.get("employee_id"),
                form.get("name"),
                password=form.get("password") or DEFAULT_LIBRARIAN_PASSWORD,
                phone=form.get("phone"),
                email=form.get("email"),
                position=form.get("position"),
            )
        except ValueError as exc:
            return api_error(str(exc))
        log_event("librarian_created", user, employee_id=employee_id)
        return jsonify({"ok": True, "message": f"管理员已添加，初始密码为 {DEFAULT_LIBRARIAN_PASSWORD}"})

    if request.method == "DELETE":
        form = payload()
        employee_id = (form.get("employee_id") or "").strip()
        rows = mysql(f"SELECT librarian_no FROM librarian WHERE employee_id={q(employee_id)}", True)
        if not rows:
            return api_error("管理员不存在")
        librarian_no = rows[0]["librarian_no"]
        if int(librarian_no) == int(user["no"]):
            return api_error("不能删除当前登录的管理员账号")
        related = int(scalar(
            "SELECT "
            f"(SELECT COUNT(*) FROM borrow_record WHERE borrow_librarian_no={q(librarian_no)} OR return_librarian_no={q(librarian_no)}) + "
            f"(SELECT COUNT(*) FROM reservation WHERE handled_by_no={q(librarian_no)}) + "
            f"(SELECT COUNT(*) FROM book_media WHERE uploaded_by_no={q(librarian_no)}) c",
            0,
        ))
        if related:
            mysql(f"UPDATE librarian SET status='disabled' WHERE librarian_no={q(librarian_no)}")
            log_event("librarian_disabled", user, employee_id=employee_id)
            return jsonify({"ok": True, "message": "该管理员已有业务记录，已停用账号"})
        mysql(f"DELETE FROM librarian WHERE librarian_no={q(librarian_no)}")
        log_event("librarian_deleted", user, employee_id=employee_id)
        return jsonify({"ok": True, "message": "管理员已删除"})

    employee_id = (request.args.get("employee_id") or "").strip()
    name = (request.args.get("name") or "").strip()
    where = []
    if employee_id:
        where.append(f"employee_id LIKE {q('%' + employee_id + '%')}")
    if name:
        where.append(f"name LIKE {q('%' + name + '%')}")
    where_sql = " WHERE " + " AND ".join(where) if where else ""
    rows, pagination = paginate(
        "SELECT employee_id,name,phone,email,position,status,created_at "
        f"FROM librarian{where_sql} ORDER BY employee_id",
        f"SELECT COUNT(*) c FROM librarian{where_sql}",
    )
    return jsonify({"ok": True, "rows": rows, "pagination": pagination})
