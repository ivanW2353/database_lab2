from functools import wraps
import re

from flask import jsonify, request, session


def current_user():
    user = session.get("user")
    return user if isinstance(user, dict) else None


def payload():
    return request.get_json(silent=True) or request.form.to_dict()


def api_error(message, status=400):
    return jsonify({"ok": False, "message": message}), status


def db_api_error(exc):
    raw = str(exc)
    translations = {
        "Book copy is not available": "该馆藏副本当前不可借",
        "Borrow limit exceeded": "已达到最大借阅数量，不能继续借出",
        "Student has unpaid overdue fine": "存在未缴违期罚金，不能借出",
        "Student already has an active reservation for this book": "该图书已有有效预约记录",
        "Invalid USTC undergraduate student id": "学号不符合中科大本科生学号格式",
        "foreign key constraint fails": "提交的数据不存在或已被删除",
    }
    for key, message in translations.items():
        if key in raw:
            return api_error(message)
    lines = [line for line in raw.splitlines() if "Using a password" not in line]
    message = lines[-1] if lines else raw
    message = re.sub(r"^ERROR\s+\d+\s+\([^)]+\)\s+at line \d+:\s*", "", message)
    return api_error(f"数据库操作失败：{message}")


def require_api_role(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = current_user()
            if not user or user.get("role") != role:
                return api_error("请先登录", 401)
            return func(user, *args, **kwargs)

        return wrapper

    return decorator
