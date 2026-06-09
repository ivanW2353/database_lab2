from backend.mysql_cli import mysql, q, scalar
from tests.helpers import ApiTestCase


class ReservationApiTest(ApiTestCase):
    def test_student_reservation_list_is_paginated(self):
        student_id = self.create_student("40")
        self.login_student(student_id)

        response = self.client.get("/api/student/reservations?page=1&page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.json["pagination"]["page_size"]), 1)

    def test_student_can_cancel_waiting_reservation(self):
        student_id = self.create_student("41")
        book_no = self.create_book("41", copies=1)
        self.login_student(student_id)
        reserved = self.client.post("/api/student/reservations", json={
            "book_no": book_no,
            "borrow_date": "2099-01-01",
        })
        self.assertEqual(reserved.status_code, 200)
        reservation_code = scalar(
            "SELECT r.reservation_code FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id={q(student_id)} AND r.book_no={book_no} ORDER BY r.reservation_no DESC LIMIT 1"
        )
        self.assertRegex(reservation_code, r"^RV\d{12}$")
        reservation_no = scalar(
            "SELECT r.reservation_no FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id={q(student_id)} AND r.book_no={book_no} ORDER BY r.reservation_no DESC LIMIT 1"
        )

        response = self.client.delete("/api/student/reservations", json={"reservation_no": reservation_no})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(scalar(f"SELECT status FROM reservation WHERE reservation_no={q(reservation_no)}"), "cancelled")

    def test_rejects_cancel_for_finished_reservation(self):
        student_id = self.create_student("42")
        book_no = self.create_book("42", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/reservations", json={"book_no": book_no, "borrow_date": "2099-01-01"})
        reservation_no = scalar(
            "SELECT r.reservation_no FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id={q(student_id)} AND r.book_no={book_no} ORDER BY r.reservation_no DESC LIMIT 1"
        )
        self.client.delete("/api/student/reservations", json={"reservation_no": reservation_no})

        response = self.client.delete("/api/student/reservations", json={"reservation_no": reservation_no})

        self.assertEqual(response.status_code, 400)

    def test_student_can_update_own_active_reservation_date(self):
        student_id = self.create_student("43")
        book_no = self.create_book("43", copies=1)
        self.login_student(student_id)
        self.client.post("/api/student/reservations", json={"book_no": book_no, "borrow_date": "2099-01-01"})
        reservation_no = scalar(
            "SELECT r.reservation_no FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id={q(student_id)} AND r.book_no={book_no} ORDER BY r.reservation_no DESC LIMIT 1"
        )

        response = self.client.put("/api/student/reservations", json={
            "reservation_no": reservation_no,
            "borrow_date": "2099-02-01",
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(scalar(f"SELECT borrow_date FROM reservation WHERE reservation_no={q(reservation_no)}"), "2099-02-01")
        self.assertEqual(scalar(f"SELECT DATE(expire_at) FROM reservation WHERE reservation_no={q(reservation_no)}"), "2099-02-02")

    def test_student_cannot_update_finished_or_another_students_reservation(self):
        owner_id = self.create_student("44")
        other_id = self.create_student("45")
        book_no = self.create_book("44", copies=1)
        self.login_student(owner_id)
        self.client.post("/api/student/reservations", json={"book_no": book_no, "borrow_date": "2099-01-01"})
        reservation_no = scalar(
            "SELECT r.reservation_no FROM reservation r JOIN student s ON s.student_no=r.student_no "
            f"WHERE s.student_id={q(owner_id)} AND r.book_no={book_no} ORDER BY r.reservation_no DESC LIMIT 1"
        )
        self.login_student(other_id)

        other_response = self.client.put("/api/student/reservations", json={
            "reservation_no": reservation_no,
            "borrow_date": "2099-02-01",
        })
        mysql(f"UPDATE reservation SET status='fulfilled' WHERE reservation_no={q(reservation_no)}")
        self.login_student(owner_id)
        finished_response = self.client.put("/api/student/reservations", json={
            "reservation_no": reservation_no,
            "borrow_date": "2099-02-01",
        })

        self.assertEqual(other_response.status_code, 400)
        self.assertEqual(finished_response.status_code, 400)
        self.assertEqual(scalar(f"SELECT borrow_date FROM reservation WHERE reservation_no={q(reservation_no)}"), "2099-01-01")
