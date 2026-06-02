import time
import unittest

from backend import create_app
from backend.mysql_cli import mysql, q, scalar
from backend.security import hash_password


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.tag = str(int(time.time()))[-6:]

    @classmethod
    def tearDownClass(cls):
        cleanup_test_data()

    def tearDown(self):
        cleanup_test_data()

    @staticmethod
    def ensure_reference_data():
        category_no = scalar("SELECT category_no FROM book_category ORDER BY category_no LIMIT 1")
        if not category_no:
            mysql("INSERT INTO book_category (category_code,category_name) VALUES ('Z','综合性图书')")
            category_no = scalar("SELECT category_no FROM book_category WHERE category_code='Z'")
        publisher_no = scalar("SELECT publisher_no FROM publisher ORDER BY publisher_no LIMIT 1")
        if not publisher_no:
            mysql("INSERT INTO publisher (publisher_name) VALUES ('自动化测试出版社')")
            publisher_no = scalar("SELECT publisher_no FROM publisher WHERE publisher_name='自动化测试出版社'")
        return category_no, publisher_no

    def create_student(self, suffix="01"):
        student_id = f"pb{self.tag}{suffix}".ljust(10, "0")[:10]
        mysql(
            "INSERT INTO student (student_id,password_hash,name,phone,email,student_type) "
            f"VALUES ({q(student_id)},{q(hash_password('123456'))},'自动化测试学生','13800000000',"
            f"{q(student_id + '@example.com')},'undergraduate')"
        )
        return student_id

    def create_book(self, suffix="01", copies=1):
        category_no, publisher_no = self.ensure_reference_data()
        isbn = f"T{self.tag}{suffix}"
        mysql(
            "INSERT INTO book (isbn,title,category_no,publisher_no,language,summary) "
            f"VALUES ({q(isbn)},{q('自动化测试图书' + suffix)},{q(category_no)},{q(publisher_no)},'Chinese','测试用书')"
        )
        book_no = int(scalar(f"SELECT book_no FROM book WHERE isbn={q(isbn)}"))
        for index in range(copies):
            barcode = f"TC{self.tag}{suffix}{index}"
            mysql(
                "INSERT INTO book_copy (book_no,barcode,location) "
                f"VALUES ({book_no},{q(barcode)},'自动化测试书库')"
            )
        return book_no

    def login_student(self, student_id):
        return self.client.post("/api/login", json={
            "role": "student",
            "login": student_id,
            "password": "123456",
        })

    def login_admin(self):
        return self.client.post("/api/login", json={
            "role": "librarian",
            "login": "admin",
            "password": "123456",
        })


def cleanup_test_data():
    student_rows = mysql("SELECT student_no FROM student WHERE name IN ('自动化测试学生','测试学生')", True)
    book_rows = mysql("SELECT book_no FROM book WHERE title LIKE '自动化测试图书%' OR title LIKE '测试图书%'", True)
    student_list = ",".join(str(row["student_no"]) for row in student_rows) or "NULL"
    book_list = ",".join(str(row["book_no"]) for row in book_rows) or "NULL"
    copy_no_sql = f"SELECT copy_no FROM book_copy WHERE book_no IN ({book_list})"
    borrow_rows = mysql(
        "SELECT borrow_no FROM borrow_record "
        f"WHERE student_no IN ({student_list}) OR copy_no IN ({copy_no_sql})",
        True,
    )
    borrow_list = ",".join(str(row["borrow_no"]) for row in borrow_rows) or "NULL"
    mysql(f"DELETE FROM overdue_record WHERE borrow_no IN ({borrow_list})")
    mysql(f"DELETE FROM borrow_record WHERE borrow_no IN ({borrow_list})")
    mysql(f"DELETE FROM reservation WHERE student_no IN ({student_list}) OR book_no IN ({book_list})")
    mysql(f"DELETE FROM book_media WHERE book_no IN ({book_list})")
    mysql(f"DELETE FROM book_author WHERE book_no IN ({book_list})")
    mysql(f"DELETE FROM book_copy WHERE book_no IN ({book_list})")
    mysql(f"DELETE FROM book WHERE book_no IN ({book_list})")
    mysql(f"DELETE FROM student WHERE student_no IN ({student_list})")
