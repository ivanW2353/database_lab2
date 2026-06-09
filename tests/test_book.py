from io import BytesIO
from pathlib import Path

from backend.config import BASE_DIR
from backend.mysql_cli import mysql, scalar
from tests.helpers import ApiTestCase


class BookApiTest(ApiTestCase):
    def test_search_book_by_title(self):
        book_no = self.create_book("21", copies=1)
        title = scalar(f"SELECT title FROM book WHERE book_no={book_no}")

        response = self.client.get(f"/api/books?q={title}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(int(book["book_no"]) == book_no for book in response.json["books"]))

    def test_search_book_by_category(self):
        book_no = self.create_book("22", copies=1)
        category_code = scalar(
            "SELECT c.category_code FROM book b JOIN book_category c ON c.category_no=b.category_no "
            f"WHERE b.book_no={book_no}"
        )

        response = self.client.get(f"/api/books?category_code={category_code}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(int(book["book_no"]) == book_no for book in response.json["books"]))

    def test_book_list_uses_database_pagination(self):
        self.create_book("27", copies=1)
        self.create_book("28", copies=1)

        response = self.client.get("/api/books?page=1&page_size=2")

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.json["books"]), 2)
        self.assertEqual(int(response.json["pagination"]["page_size"]), 2)
        self.assertGreaterEqual(int(response.json["pagination"]["total"]), 2)
        self.assertGreaterEqual(int(response.json["pagination"]["total_pages"]), 1)

    def test_admin_book_options_are_not_limited_by_page(self):
        self.create_book("29", copies=1)
        self.login_admin()

        response = self.client.get("/api/admin/books?page=1&page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["books"]), 1)
        self.assertGreaterEqual(len(response.json["book_options"]), int(response.json["pagination"]["total"]))

    def test_admin_book_detail_includes_borrow_records(self):
        student_id = self.create_student("30")
        book_no = self.create_book("30", copies=1)
        copy_no = scalar(f"SELECT copy_no FROM book_copy WHERE book_no={book_no}")
        student_no = scalar(f"SELECT student_no FROM student WHERE student_id='{student_id}'")
        mysql(
            "INSERT INTO borrow_record (student_no,copy_no,borrow_time,due_time,status) "
            f"VALUES ({student_no},{copy_no},NOW(),DATE_ADD(NOW(),INTERVAL 30 DAY),'borrowed')"
        )
        self.login_admin()

        response = self.client.get(f"/api/admin/books/{book_no}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["book"]["borrow_records"]), 1)
        record = response.json["book"]["borrow_records"][0]
        self.assertEqual(record["student_id"], student_id)
        self.assertRegex(record["borrow_code"], r"^BR\d{12}$")

    def test_public_book_detail_does_not_include_borrow_records(self):
        book_no = self.create_book("31", copies=1)

        response = self.client.get(f"/api/books/{book_no}")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("borrow_records", response.json["book"])

    def test_admin_media_upload_requires_book_and_file(self):
        self.login_admin()

        response = self.client.post("/api/admin/books", data={"action": "media"}, content_type="multipart/form-data")

        self.assertEqual(response.status_code, 400)

    def test_admin_copy_defaults_purchase_date_to_today(self):
        book_no = self.create_book("24", copies=0)
        self.login_admin()

        response = self.client.post("/api/admin/books", json={
            "action": "copy",
            "book_no": book_no,
            "barcode": f"DEFAULT-DATE-{book_no}",
            "location": "测试书库",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            scalar(f"SELECT purchase_date=CURDATE() FROM book_copy WHERE barcode='DEFAULT-DATE-{book_no}'"),
            "1",
        )

    def test_admin_can_upload_local_media_file(self):
        book_no = self.create_book("25", copies=1)
        self.login_admin()
        saved_path = None
        response = None
        try:
            response = self.client.post("/api/admin/books", data={
                "action": "media",
                "book_no": str(book_no),
                "file": (BytesIO(b"fake png content"), "local-cover.png"),
            }, content_type="multipart/form-data")

            self.assertEqual(response.status_code, 200)
            saved_path = scalar(f"SELECT file_path FROM book_media WHERE book_no={book_no}")
            self.assertTrue(saved_path.startswith(f"uploads/books/{book_no}/"))
            self.assertTrue((BASE_DIR / Path(saved_path)).is_file())
            self.assertEqual(scalar(f"SELECT title FROM book_media WHERE book_no={book_no}"), "local-cover.png")
            self.assertEqual(scalar(f"SELECT mime_type FROM book_media WHERE book_no={book_no}"), "image/png")
            self.assertEqual(int(scalar(f"SELECT file_size FROM book_media WHERE book_no={book_no}")), 16)
        finally:
            if response:
                response.close()
            if saved_path:
                (BASE_DIR / Path(saved_path)).unlink(missing_ok=True)

    def test_admin_can_update_book_summary(self):
        book_no = self.create_book("26", copies=1)
        self.login_admin()

        response = self.client.post("/api/admin/books", json={
            "action": "summary",
            "book_no": book_no,
            "summary": "修改后的数据库课程图书简介",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(scalar(f"SELECT summary FROM book WHERE book_no={book_no}"), "修改后的数据库课程图书简介")

    def test_admin_update_summary_rejects_missing_book(self):
        self.login_admin()

        response = self.client.post("/api/admin/books", json={
            "action": "summary",
            "book_no": 999999999,
            "summary": "不存在的图书",
        })

        self.assertEqual(response.status_code, 400)
