import unittest

from backend.mysql_cli import like, q
from backend.models import Student
from backend.security import hash_password, validate_password, verify_password
from backend.services import validate_student_id
from backend.validators import validate_email, validate_phone


class BackendUtilsTest(unittest.TestCase):
    def test_sql_quote_escapes_single_quote(self):
        self.assertEqual(q("O'Reilly"), "'O''Reilly'")

    def test_like_escapes_wildcards(self):
        self.assertEqual(like("a%b_c"), "%a\\%b\\_c%")

    def test_password_hash_verification(self):
        stored = hash_password("123456")
        self.assertTrue(verify_password("123456", stored))
        self.assertFalse(verify_password("wrong", stored))

    def test_password_policy(self):
        self.assertTrue(validate_password("abc123"))
        self.assertTrue(validate_password("123456"))
        self.assertTrue(validate_password("abcdef"))
        self.assertFalse(validate_password("abc12"))
        self.assertFalse(validate_password("abc-123"))
        self.assertFalse(validate_password("中文123456"))

    def test_student_model_defaults(self):
        self.assertEqual(Student.__table__.c.student_type.default.arg, "undergraduate")
        self.assertEqual(Student.__table__.c.status.default.arg, "normal")

    def test_ustc_undergrad_student_id_validation(self):
        self.assertTrue(validate_student_id("pb22000001"))
        self.assertTrue(validate_student_id("PB22000001"))
        self.assertFalse(validate_student_id("22000001"))
        self.assertFalse(validate_student_id("pb220001"))

    def test_contact_validation(self):
        self.assertTrue(validate_phone("13800000000"))
        self.assertTrue(validate_phone("0551-63600000"))
        self.assertTrue(validate_email("student@example.com"))
        self.assertFalse(validate_phone("12345"))
        self.assertFalse(validate_phone("abc13800000000"))
        self.assertFalse(validate_email("student@example"))
        self.assertFalse(validate_email("student@@example.com"))


if __name__ == "__main__":
    unittest.main()
