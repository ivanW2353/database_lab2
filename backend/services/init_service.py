from ..config import BASE_DIR, UPLOAD_DIR
from ..mysql_cli import mysql, q, scalar
from ..security import hash_password


def ensure_demo_accounts():
    if int(scalar("SELECT COUNT(*) c FROM librarian", 0)) == 0:
        mysql(
            "INSERT INTO librarian (employee_id,password_hash,name,phone,email,position) "
            f"VALUES ('admin',{q(hash_password('123456'))},'系统管理员','0551-63600000','admin@example.com','馆长')"
        )
    if int(scalar("SELECT COUNT(*) c FROM student", 0)) == 0:
        mysql(
            "INSERT INTO student (student_id,password_hash,name,gender,college,major,phone,email,student_type) "
            f"VALUES ('pb22000001',{q(hash_password('123456'))},'演示学生','other','计算机科学与技术学院','计算机科学与技术','13800000000','student@example.com','undergraduate')"
        )
    if int(scalar("SELECT COUNT(*) c FROM book_media", 0)) == 0:
        UPLOAD_DIR.mkdir(exist_ok=True)
        sample = UPLOAD_DIR / "sample-book-cover.txt"
        sample.write_text("图书封面示例文件", encoding="utf-8")
        mysql(
            "INSERT INTO book_media (book_no, media_type, title, file_path, mime_type, file_size, uploaded_by_no) "
            f"VALUES (1,'file','示例附件',{q(str(sample.relative_to(BASE_DIR)))},'text/plain',{sample.stat().st_size},1)"
        )
