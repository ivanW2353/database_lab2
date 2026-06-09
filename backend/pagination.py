from flask import request

from .mysql_cli import mysql, scalar


def paginate(rows_sql, count_sql, default_page_size=10):
    try:
        page = max(1, int(request.args.get("page", 1)))
        page_size = min(100, max(1, int(request.args.get("page_size", default_page_size))))
    except (TypeError, ValueError):
        page, page_size = 1, default_page_size
    total = int(scalar(count_sql, 0))
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = min(page, total_pages)
    rows = mysql(f"{rows_sql} LIMIT {page_size} OFFSET {(page - 1) * page_size}", True)
    return rows, {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }
