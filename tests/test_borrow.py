from backend.mysql_cli import scalar
from tests.helpers import ApiTestCase


class BorrowApiTest(ApiTestCase):
    def test_student_borrow_updates_copy_status(self):
        student_id = self.create_student("31")
        book_no = self.create_book("31", copies=1)
        self.login_student(student_id)

        response = self.client.post("/api/student/borrows", json={"book_no": book_no})

        self.assertEqual(response.status_code, 200)
        self.assertIn("借出成功", response.json["message"])
        self.assertEqual(scalar(f"SELECT status FROM book_copy WHERE book_no={book_no}"), "borrowed")

    def test_student_borrow_without_stock_joins_waitlist(self):
        student_id = self.create_student("32")
        book_no = self.create_book("32", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/borrows", json={"book_no": book_no})

        response = self.client.post("/api/student/borrows", json={"book_no": book_no})

        self.assertEqual(response.status_code, 200)
        self.assertIn("预约队列", response.json["message"])
        count = int(scalar(
            "SELECT COUNT(*) c FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id='{student_id}' AND r.book_no={book_no} AND r.status='waiting'",
            0,
        ))
        self.assertGreaterEqual(count, 1)
