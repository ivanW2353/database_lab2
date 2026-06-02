from backend.mysql_cli import scalar
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
