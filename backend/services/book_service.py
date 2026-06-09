from ..mysql_cli import like, mysql, q


def book_categories():
    return mysql(
        "SELECT category_no,category_code,category_name "
        "FROM book_category WHERE parent_no IS NULL ORDER BY category_code",
        True,
    )


def book_rows(keyword="", category_no="", category_code="", page=None, page_size=10):
    conditions = []
    if keyword:
        lk = q(like(keyword))
        conditions.append(f"(b.title LIKE {lk} ESCAPE '\\\\' OR b.isbn LIKE {lk} ESCAPE '\\\\' OR a.author_name LIKE {lk} ESCAPE '\\\\')")
    if category_no:
        conditions.append(f"(b.category_no={q(category_no)} OR c.parent_no={q(category_no)})")
    category_codes = [code.strip() for code in str(category_code or "").split(",") if code.strip()]
    if category_codes:
        code_list = ",".join(q(code) for code in category_codes)
        conditions.append(f"(c.category_code IN ({code_list}) OR parent.category_code IN ({code_list}))")
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    pagination = {}
    limit = ""
    if page is not None:
        try:
            page = max(1, int(page))
            page_size = min(100, max(1, int(page_size)))
        except (TypeError, ValueError):
            page, page_size = 1, 10
        total = int(mysql(f"""
SELECT COUNT(DISTINCT b.book_no) total
FROM book b
JOIN book_category c ON c.category_no=b.category_no
LEFT JOIN book_category parent ON parent.category_no=c.parent_no
LEFT JOIN book_author ba ON ba.book_no=b.book_no
LEFT JOIN author a ON a.author_no=ba.author_no
{where}
""", True)[0]["total"])
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = min(page, total_pages)
        limit = f"LIMIT {page_size} OFFSET {(page - 1) * page_size}"
        pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": total_pages}
    rows = mysql(f"""
SELECT b.book_no,b.isbn,b.title,c.category_name,COALESCE(p.publisher_name,'') publisher_name,
       COALESCE(GROUP_CONCAT(DISTINCT a.author_name ORDER BY ba.author_order SEPARATOR ', '),'') authors,
       COUNT(bc.copy_no) copy_count,
       SUM(CASE WHEN bc.status='available' THEN 1 ELSE 0 END) available_count
FROM book b
JOIN book_category c ON c.category_no=b.category_no
LEFT JOIN book_category parent ON parent.category_no=c.parent_no
LEFT JOIN publisher p ON p.publisher_no=b.publisher_no
LEFT JOIN book_author ba ON ba.book_no=b.book_no
LEFT JOIN author a ON a.author_no=ba.author_no
LEFT JOIN book_copy bc ON bc.book_no=b.book_no
{where}
GROUP BY b.book_no,b.isbn,b.title,c.category_name,p.publisher_name
ORDER BY b.book_no
{limit}
""", True)
    return (rows, pagination) if page is not None else rows


def top_borrowed_books(limit=10):
    return mysql(f"""
SELECT b.book_no,b.isbn,b.title,
       COALESCE(GROUP_CONCAT(DISTINCT a.author_name ORDER BY ba.author_order SEPARATOR ', '),'') authors,
       COUNT(br.borrow_no) borrow_count
FROM borrow_record br
JOIN book_copy bc ON bc.copy_no=br.copy_no
JOIN book b ON b.book_no=bc.book_no
LEFT JOIN book_author ba ON ba.book_no=b.book_no
LEFT JOIN author a ON a.author_no=ba.author_no
GROUP BY b.book_no,b.isbn,b.title
ORDER BY borrow_count DESC,b.book_no ASC
LIMIT {int(limit)}
""", True)


def book_detail(book_no):
    rows = mysql(f"""
SELECT b.book_no,b.isbn,b.title,b.publish_date,b.edition,b.price,b.language,b.summary,
       c.category_code,c.category_name,COALESCE(p.publisher_name,'') publisher_name,
       COALESCE(p.address,'') publisher_address,COALESCE(p.phone,'') publisher_phone,
       COALESCE(GROUP_CONCAT(DISTINCT a.author_name ORDER BY ba.author_order SEPARATOR ', '),'') authors
FROM book b
JOIN book_category c ON c.category_no=b.category_no
LEFT JOIN publisher p ON p.publisher_no=b.publisher_no
LEFT JOIN book_author ba ON ba.book_no=b.book_no
LEFT JOIN author a ON a.author_no=ba.author_no
WHERE b.book_no={q(book_no)}
GROUP BY b.book_no,b.isbn,b.title,b.publish_date,b.edition,b.price,b.language,b.summary,
         c.category_code,c.category_name,p.publisher_name,p.address,p.phone
""", True)
    if not rows:
        return None
    detail = rows[0]
    detail["copies"] = mysql(
        "SELECT copy_no,barcode,location,status,purchase_date "
        f"FROM book_copy WHERE book_no={q(book_no)} ORDER BY copy_no",
        True,
    )
    detail["media"] = mysql(
        "SELECT media_no,media_type,title,file_path,mime_type,file_size,uploaded_at "
        f"FROM book_media WHERE book_no={q(book_no)} ORDER BY media_no",
        True,
    )
    return detail


def book_borrow_records(book_no):
    return mysql(f"""
SELECT br.borrow_no,br.borrow_code,s.student_id,s.name,bc.barcode,
       br.borrow_time,br.due_time,br.return_time,br.renew_count,br.status
FROM borrow_record br
JOIN student s ON s.student_no=br.student_no
JOIN book_copy bc ON bc.copy_no=br.copy_no
WHERE bc.book_no={q(book_no)}
ORDER BY br.borrow_no DESC
""", True)
