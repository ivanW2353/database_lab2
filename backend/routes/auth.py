from flask import Blueprint, jsonify, session

from ..audit import log_event
from ..security import verify_password
from ..services import create_student_with_id, find_login_user
from .helpers import api_error, current_user, payload


auth_api_bp = Blueprint("auth", __name__)


@auth_api_bp.route("/")
def api_root():
    return jsonify({"ok": True, "message": "Library API is running"})


@auth_api_bp.route("/api/me")
def api_me():
    return jsonify({"ok": True, "user": current_user()})


@auth_api_bp.route("/api/login", methods=["POST"])
def api_login():
    data = payload()
    role = data.get("role", "student")
    login_name = data.get("login", "")
    password = data.get("password", "")
    rows = find_login_user(role, login_name)
    if rows and verify_password(password, rows[0]["password_hash"]):
        session["user"] = {"role": role, "no": rows[0]["no"], "login": rows[0]["login"], "name": rows[0]["name"]}
        log_event("login_success", session["user"])
        return jsonify({"ok": True, "user": session["user"]})
    log_event("login_failed", role=role, login=login_name)
    return api_error("账号或密码错误", 401)


@auth_api_bp.route("/api/register/student", methods=["POST"])
def api_student_register():
    data = payload()
    student_id = data.get("student_id", "")
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")
    if password != confirm_password:
        return api_error("两次输入的密码不一致")
    try:
        normalized_id = create_student_with_id(student_id, password=password)
    except ValueError as exc:
        return api_error(str(exc))
    rows = find_login_user("student", normalized_id)
    session["user"] = {"role": "student", "no": rows[0]["no"], "login": rows[0]["login"], "name": rows[0]["name"]}
    log_event("student_registered", session["user"])
    log_event("login_success", session["user"])
    return jsonify({"ok": True, "message": "注册成功", "user": session["user"]})


@auth_api_bp.route("/api/logout", methods=["POST"])
def api_logout():
    user = current_user()
    if user:
        log_event("logout", user)
    session.clear()
    return jsonify({"ok": True})
