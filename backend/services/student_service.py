import re

from ..mysql_cli import mysql, q, scalar
from ..security import PASSWORD_POLICY_MESSAGE, hash_password, validate_password


PLACEHOLDER_STUDENT_NAME = "待完善"
DEFAULT_STUDENT_PASSWORD = "123456"
USTC_UNDERGRAD_STUDENT_ID = re.compile(r"^(PB|JL|XK|XJ|NS|PL)\d{8}$", re.IGNORECASE)


def validate_student_id(student_id):
    return bool(student_id and USTC_UNDERGRAD_STUDENT_ID.fullmatch(student_id.strip()))


def create_student_with_id(student_id, password=None):
    normalized_id = (student_id or "").strip()
    if not validate_student_id(normalized_id):
        raise ValueError("学号格式不符合中科大本科生学号要求")
    exists = scalar(f"SELECT student_no FROM student WHERE LOWER(student_id)=LOWER({q(normalized_id)})")
    if exists:
        raise ValueError("该学号已注册")
    initial_password = password or DEFAULT_STUDENT_PASSWORD
    if not validate_password(initial_password):
        raise ValueError(PASSWORD_POLICY_MESSAGE)
    mysql(
        "INSERT INTO student (student_id,password_hash,name,gender,student_type,status) "
        f"VALUES ({q(normalized_id)},{q(hash_password(initial_password))},"
        f"{q(PLACEHOLDER_STUDENT_NAME)},'other','undergraduate','normal')"
    )
    return normalized_id
