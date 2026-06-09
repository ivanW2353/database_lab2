from backend.mysql_cli import mysql, q, scalar
from tests.helpers import ApiTestCase


class BorrowApiTest(ApiTestCase):
    def test_student_borrow_list_is_paginated(self):
        student_id = self.create_student("30")
        self.login_student(student_id)

        response = self.client.get("/api/student/borrows?page=1&page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.json["pagination"]["page_size"]), 1)

    def test_student_borrow_updates_copy_status(self):
        student_id = self.create_student("31")
        book_no = self.create_book("31", copies=1)
        self.login_student(student_id)

        response = self.client.post("/api/student/borrows", json={"book_no": book_no})

        self.assertEqual(response.status_code, 200)
        self.assertIn("借出成功", response.json["message"])
        self.assertEqual(scalar(f"SELECT status FROM book_copy WHERE book_no={book_no}"), "borrowed")
        borrow_code = scalar(
            "SELECT br.borrow_code FROM borrow_record br JOIN student s ON s.student_no=br.student_no "
            f"WHERE s.student_id={q(student_id)} ORDER BY br.borrow_no DESC LIMIT 1"
        )
        self.assertRegex(borrow_code, r"^BR\d{12}$")

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

    def test_student_can_renew_own_active_borrow(self):
        student_id = self.create_student("33")
        book_no = self.create_book("33", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/borrows", json={"book_no": book_no})
        borrow_no = scalar(
            "SELECT br.borrow_no FROM borrow_record br "
            "JOIN student s ON s.student_no=br.student_no "
            f"WHERE s.student_id={q(student_id)} AND br.status='borrowed'"
        )
        old_due_time = scalar(f"SELECT due_time FROM borrow_record WHERE borrow_no={q(borrow_no)}")

        response = self.client.post("/api/student/borrows/renew", json={"borrow_no": borrow_no})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(scalar(f"SELECT renew_count FROM borrow_record WHERE borrow_no={q(borrow_no)}")), 1)
        self.assertGreater(scalar(f"SELECT due_time FROM borrow_record WHERE borrow_no={q(borrow_no)}"), old_due_time)

    def test_student_can_return_own_borrow(self):
        student_id = self.create_student("34")
        book_no = self.create_book("34", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/borrows", json={"book_no": book_no})
        borrow_no = scalar(
            "SELECT br.borrow_no FROM borrow_record br "
            "JOIN student s ON s.student_no=br.student_no "
            f"WHERE s.student_id={q(student_id)} AND br.status='borrowed'"
        )

        response = self.client.post("/api/student/borrows/return", json={"borrow_no": borrow_no})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(scalar(f"SELECT status FROM borrow_record WHERE borrow_no={q(borrow_no)}"), "returned")
        self.assertEqual(scalar(f"SELECT status FROM book_copy WHERE book_no={book_no}"), "available")

    def test_student_cannot_renew_past_due_borrow(self):
        student_id = self.create_student("37")
        book_no = self.create_book("37", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/borrows", json={"book_no": book_no})
        borrow_no = scalar(
            "SELECT br.borrow_no FROM borrow_record br "
            "JOIN student s ON s.student_no=br.student_no "
            f"WHERE s.student_id={q(student_id)} AND br.status='borrowed'"
        )
        mysql(f"UPDATE borrow_record SET due_time=DATE_SUB(NOW(), INTERVAL 1 DAY) WHERE borrow_no={q(borrow_no)}")

        response = self.client.post("/api/student/borrows/renew", json={"borrow_no": borrow_no})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(int(scalar(f"SELECT renew_count FROM borrow_record WHERE borrow_no={q(borrow_no)}")), 0)

    def test_student_cannot_operate_another_students_borrow(self):
        owner_id = self.create_student("35")
        other_id = self.create_student("36")
        book_no = self.create_book("35", copies=1)
        self.login_student(owner_id)
        self.client.post("/api/student/borrows", json={"book_no": book_no})
        borrow_no = scalar(
            "SELECT br.borrow_no FROM borrow_record br "
            "JOIN student s ON s.student_no=br.student_no "
            f"WHERE s.student_id={q(owner_id)} AND br.status='borrowed'"
        )
        self.login_student(other_id)

        renewed = self.client.post("/api/student/borrows/renew", json={"borrow_no": borrow_no})
        returned = self.client.post("/api/student/borrows/return", json={"borrow_no": borrow_no})

        self.assertEqual(renewed.status_code, 400)
        self.assertEqual(returned.status_code, 400)
        self.assertEqual(scalar(f"SELECT status FROM borrow_record WHERE borrow_no={q(borrow_no)}"), "borrowed")
