from backend.mysql_cli import q, scalar, mysql
from tests.helpers import ApiTestCase


class AdminFlowTest(ApiTestCase):
    def test_admin_borrow_return_and_pay_overdue(self):
        student_id = self.create_student("51")
        book_no = self.create_book("51", copies=1)
        barcode = scalar(f"SELECT barcode FROM book_copy WHERE book_no={book_no}")
        self.login_admin()

        borrowed = self.client.post("/api/admin/borrow", json={"student_id": student_id, "barcode": barcode})
        self.assertEqual(borrowed.status_code, 200)
        borrow_no = scalar(
            "SELECT br.borrow_no FROM borrow_record br "
            "JOIN student s ON s.student_no=br.student_no "
            "JOIN book_copy bc ON bc.copy_no=br.copy_no "
            f"WHERE s.student_id={q(student_id)} AND bc.barcode={q(barcode)}"
        )
        mysql(f"UPDATE borrow_record SET due_time=DATE_SUB(NOW(), INTERVAL 2 DAY) WHERE borrow_no={q(borrow_no)}")

        returned = self.client.post("/api/admin/return", json={"borrow_no": borrow_no})
        self.assertEqual(returned.status_code, 200)
        self.assertEqual(scalar(f"SELECT status FROM book_copy WHERE barcode={q(barcode)}"), "available")

        overdue_no = scalar(f"SELECT overdue_no FROM overdue_record WHERE borrow_no={q(borrow_no)}")
        self.assertIsNotNone(overdue_no)

        paid = self.client.post("/api/admin/overdue", json={"overdue_no": overdue_no})
        self.assertEqual(paid.status_code, 200)
        self.assertEqual(scalar(f"SELECT status FROM overdue_record WHERE overdue_no={q(overdue_no)}"), "paid")
