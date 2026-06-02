from backend.mysql_cli import q, scalar
from tests.helpers import ApiTestCase


class ReservationApiTest(ApiTestCase):
    def test_student_can_cancel_waiting_reservation(self):
        student_id = self.create_student("41")
        book_no = self.create_book("41", copies=1)
        self.login_student(student_id)
        reserved = self.client.post("/api/student/reservations", json={
            "book_no": book_no,
            "borrow_date": "2099-01-01",
        })
        self.assertEqual(reserved.status_code, 200)
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
