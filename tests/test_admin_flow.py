from backend.mysql_cli import q, scalar, mysql
from tests.helpers import ApiTestCase


class AdminFlowTest(ApiTestCase):
    def test_admin_student_list_uses_student_id_and_detail_includes_borrows(self):
        student_id = self.create_student("50")
        book_no = self.create_book("50", copies=1)
        barcode = scalar(f"SELECT barcode FROM book_copy WHERE book_no={book_no}")
        self.login_admin()
        self.client.post("/api/admin/borrow", json={"student_id": student_id, "barcode": barcode})

        student_list = self.client.get("/api/admin/students?page=1&page_size=100")
        detail = self.client.get(f"/api/admin/students/{student_id}")

        self.assertEqual(student_list.status_code, 200)
        listed = next(row for row in student_list.json["rows"] if row["student_id"] == student_id)
        self.assertNotIn("student_no", listed)
        listed_ids = [row["student_id"] for row in student_list.json["rows"]]
        self.assertEqual(listed_ids, sorted(listed_ids))
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json["student"]["student_id"], student_id)
        self.assertEqual(len(detail.json["student"]["borrow_records"]), 1)
        self.assertRegex(detail.json["student"]["borrow_records"][0]["borrow_code"], r"^BR\d{12}$")

    def test_admin_librarian_list_uses_employee_id_order(self):
        self.login_admin()

        response = self.client.get("/api/admin/librarians?page=1&page_size=100")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json["rows"])
        self.assertTrue(all("librarian_no" not in row for row in response.json["rows"]))
        employee_ids = [row["employee_id"] for row in response.json["rows"]]
        self.assertEqual(employee_ids, sorted(employee_ids))

    def test_admin_target_lists_are_paginated(self):
        self.create_student("52")
        self.create_book("52", copies=2)
        self.login_admin()

        for path in (
            "/api/admin/students",
            "/api/admin/librarians",
            "/api/admin/borrow",
            "/api/admin/return",
            "/api/admin/reservations",
        ):
            response = self.client.get(f"{path}?page=1&page_size=1")
            self.assertEqual(response.status_code, 200, path)
            self.assertLessEqual(len(response.json["rows"]), 1, path)
            self.assertEqual(int(response.json["pagination"]["page_size"]), 1, path)

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
        self.assertRegex(scalar(f"SELECT overdue_code FROM overdue_record WHERE overdue_no={q(overdue_no)}"), r"^OD\d{12}$")
        overdue_list = self.client.get("/api/admin/overdue")
        overdue_row = next(row for row in overdue_list.json["rows"] if int(row["overdue_no"]) == int(overdue_no))
        self.assertEqual(
            overdue_row["overdue_start_date"],
            scalar(f"SELECT DATE(DATE_ADD(due_time,INTERVAL 1 DAY)) FROM borrow_record WHERE borrow_no={q(borrow_no)}"),
        )

        paid = self.client.post("/api/admin/overdue", json={"overdue_no": overdue_no})
        self.assertEqual(paid.status_code, 200)
        self.assertEqual(scalar(f"SELECT status FROM overdue_record WHERE overdue_no={q(overdue_no)}"), "paid")

    def test_admin_return_list_can_search_records(self):
        student_id = self.create_student("53")
        book_no = self.create_book("53", copies=1)
        barcode = scalar(f"SELECT barcode FROM book_copy WHERE book_no={book_no}")
        self.login_admin()
        self.client.post("/api/admin/borrow", json={"student_id": student_id, "barcode": barcode})

        found = self.client.get(f"/api/admin/return?q={barcode}&page=1&page_size=10")
        missing = self.client.get("/api/admin/return?q=NO-SUCH-RECORD&page=1&page_size=10")

        self.assertEqual(found.status_code, 200)
        self.assertEqual(len(found.json["rows"]), 1)
        self.assertEqual(found.json["rows"][0]["barcode"], barcode)
        self.assertRegex(found.json["rows"][0]["borrow_code"], r"^BR\d{12}$")
        self.assertEqual(int(missing.json["pagination"]["total"]), 0)
