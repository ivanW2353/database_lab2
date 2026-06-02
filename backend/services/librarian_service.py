from ..mysql_cli import mysql, q, scalar
from ..security import PASSWORD_POLICY_MESSAGE, hash_password, validate_password
from ..validators import validate_email, validate_phone


DEFAULT_LIBRARIAN_PASSWORD = "123456"


def create_librarian(employee_id, name, password=None, phone=None, email=None, position=None):
    normalized_id = (employee_id or "").strip()
    display_name = (name or "").strip()
    initial_password = password or DEFAULT_LIBRARIAN_PASSWORD
    if not normalized_id:
        raise ValueError("工号不能为空")
    if not display_name:
        raise ValueError("姓名不能为空")
    if not validate_password(initial_password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    if not validate_phone(phone):
        raise ValueError("电话格式不正确，请填写 11 位手机号或座机号")
    if not validate_email(email):
        raise ValueError("邮箱格式不正确")
    exists = scalar(f"SELECT librarian_no FROM librarian WHERE employee_id={q(normalized_id)}")
    if exists:
        raise ValueError("该工号已存在")
    mysql(
        "INSERT INTO librarian (employee_id,password_hash,name,phone,email,position,status) "
        f"VALUES ({q(normalized_id)},{q(hash_password(initial_password))},{q(display_name)},"
        f"{q(phone)},{q(email)},{q(position)},'normal')"
    )
    return normalized_id
