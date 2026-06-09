from sqlalchemy import BigInteger, Date, DateTime, DECIMAL, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..extensions import Base


class Student(Base):
    __tablename__ = "student"

    student_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(Enum("male", "female", "other"), default="other")
    college: Mapped[str | None] = mapped_column(String(100))
    major: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(100))
    student_type: Mapped[str] = mapped_column(Enum("undergraduate"), default="undergraduate", nullable=False)
    status: Mapped[str] = mapped_column(Enum("normal", "suspended", "cancelled"), default="normal", nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    updated_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    borrows: Mapped[list["BorrowRecord"]] = relationship(back_populates="student")
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="student")


class Librarian(Base):
    __tablename__ = "librarian"

    librarian_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    employee_id: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    email: Mapped[str | None] = mapped_column(String(100))
    position: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(Enum("normal", "disabled"), default="normal", nullable=False)


class BookCategory(Base):
    __tablename__ = "book_category"

    category_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("book_category.category_no"))
    category_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False)


class Publisher(Base):
    __tablename__ = "publisher"

    publisher_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    publisher_name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(30))


class Author(Base):
    __tablename__ = "author"

    author_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    nationality: Mapped[str | None] = mapped_column(String(80))
    biography: Mapped[str | None] = mapped_column(Text)


class Book(Base):
    __tablename__ = "book"

    book_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book_category.category_no"), nullable=False)
    publisher_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("publisher.publisher_no"))
    publish_date: Mapped[str | None] = mapped_column(Date)
    edition: Mapped[str | None] = mapped_column(String(50))
    price: Mapped[float | None] = mapped_column(DECIMAL(10, 2))
    language: Mapped[str] = mapped_column(String(50), default="Chinese")
    summary: Mapped[str | None] = mapped_column(Text)

    copies: Mapped[list["BookCopy"]] = relationship(back_populates="book")
    reservations: Mapped[list["Reservation"]] = relationship(back_populates="book")


class BookAuthor(Base):
    __tablename__ = "book_author"

    book_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book.book_no"), primary_key=True)
    author_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("author.author_no"), primary_key=True)
    author_order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class BookCopy(Base):
    __tablename__ = "book_copy"

    copy_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    book_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book.book_no"), nullable=False)
    barcode: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(Enum("available", "borrowed", "maintenance", "lost", "removed"), default="available", nullable=False)
    purchase_date: Mapped[str | None] = mapped_column(Date)

    book: Mapped[Book] = relationship(back_populates="copies")
    borrows: Mapped[list["BorrowRecord"]] = relationship(back_populates="copy")


class BorrowRule(Base):
    __tablename__ = "borrow_rule"

    rule_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_type: Mapped[str] = mapped_column(Enum("undergraduate"), unique=True, nullable=False)
    max_borrow_count: Mapped[int] = mapped_column(Integer, nullable=False)
    borrow_days: Mapped[int] = mapped_column(Integer, nullable=False)
    max_renew_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    fine_per_day: Mapped[float] = mapped_column(DECIMAL(8, 2), default=0.50, nullable=False)


class BorrowRecord(Base):
    __tablename__ = "borrow_record"

    borrow_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    borrow_code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    student_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("student.student_no"), nullable=False)
    copy_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book_copy.copy_no"), nullable=False)
    borrow_librarian_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("librarian.librarian_no"))
    return_librarian_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("librarian.librarian_no"))
    borrow_time: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    due_time: Mapped[str] = mapped_column(DateTime, nullable=False)
    return_time: Mapped[str | None] = mapped_column(DateTime)
    renew_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(Enum("borrowed", "returned", "overdue", "lost"), default="borrowed", nullable=False)

    student: Mapped[Student] = relationship(back_populates="borrows")
    copy: Mapped[BookCopy] = relationship(back_populates="borrows")


class Reservation(Base):
    __tablename__ = "reservation"

    reservation_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    reservation_code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    student_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("student.student_no"), nullable=False)
    book_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book.book_no"), nullable=False)
    reserved_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    borrow_date: Mapped[str | None] = mapped_column(Date)
    expire_at: Mapped[str | None] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Enum("waiting", "notified", "fulfilled", "cancelled", "expired"), default="waiting", nullable=False)
    handled_by_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("librarian.librarian_no"))
    handled_at: Mapped[str | None] = mapped_column(DateTime)

    student: Mapped[Student] = relationship(back_populates="reservations")
    book: Mapped[Book] = relationship(back_populates="reservations")


class OverdueRecord(Base):
    __tablename__ = "overdue_record"

    overdue_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    overdue_code: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    borrow_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("borrow_record.borrow_no"), unique=True, nullable=False)
    overdue_days: Mapped[int] = mapped_column(Integer, nullable=False)
    fine_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    paid_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), default=0.00, nullable=False)
    status: Mapped[str] = mapped_column(Enum("unpaid", "partial_paid", "paid", "waived"), default="unpaid", nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
    paid_at: Mapped[str | None] = mapped_column(DateTime)


class BookMedia(Base):
    __tablename__ = "book_media"

    media_no: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    book_no: Mapped[int] = mapped_column(BigInteger, ForeignKey("book.book_no"), nullable=False)
    media_type: Mapped[str] = mapped_column(Enum("image", "video", "file"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100))
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    uploaded_by_no: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("librarian.librarian_no"))
    uploaded_at: Mapped[str] = mapped_column(DateTime, server_default=func.current_timestamp())
