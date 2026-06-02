from ..mysql_cli import mysql, q


def find_login_user(role, login):
    if role == "student":
        return mysql(
            f"SELECT student_no no, student_id login, name, password_hash FROM student "
            f"WHERE LOWER(student_id)=LOWER({q(login)}) AND status='normal'",
            True,
        )
    return mysql(
        f"SELECT librarian_no no, employee_id login, name, password_hash FROM librarian "
        f"WHERE employee_id={q(login)} AND status='normal'",
        True,
    )
