from tests.helpers import ApiTestCase


class AuthApiTest(ApiTestCase):
    def test_rejects_anonymous_student_dashboard(self):
        response = self.client.get("/api/student/dashboard")
        self.assertEqual(response.status_code, 401)

    def test_rejects_bad_login(self):
        response = self.client.post("/api/login", json={
            "role": "student",
            "login": "missing",
            "password": "bad",
        })
        self.assertEqual(response.status_code, 401)

    def test_student_login_success(self):
        student_id = self.create_student("11")
        response = self.login_student(student_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["user"]["login"], student_id)

    def test_student_cannot_access_admin_api(self):
        student_id = self.create_student("12")
        self.login_student(student_id)
        response = self.client.get("/api/admin/dashboard")
        self.assertEqual(response.status_code, 401)
