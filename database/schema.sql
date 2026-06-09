DROP DATABASE IF EXISTS db_lab2;
CREATE DATABASE db_lab2 DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE db_lab2;

CREATE TABLE student (
  student_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(30) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  gender ENUM('male', 'female', 'other') DEFAULT 'other',
  college VARCHAR(100),
  major VARCHAR(100),
  phone VARCHAR(30),
  email VARCHAR(100),
  student_type ENUM('undergraduate') NOT NULL DEFAULT 'undergraduate',
  status ENUM('normal', 'suspended', 'cancelled') NOT NULL DEFAULT 'normal',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT chk_student_id_ustc CHECK (
    UPPER(student_id) REGEXP '^(PB|JL|XK|XJ|NS|PL)[0-9]{8}$'
  )
) ENGINE=InnoDB;

CREATE TABLE librarian (
  librarian_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  employee_id VARCHAR(30) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(50) NOT NULL,
  phone VARCHAR(30),
  email VARCHAR(100),
  position VARCHAR(100),
  status ENUM('normal', 'disabled') NOT NULL DEFAULT 'normal',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE book_category (
  category_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  parent_no BIGINT UNSIGNED NULL,
  category_code VARCHAR(30) NOT NULL UNIQUE,
  category_name VARCHAR(100) NOT NULL,
  CONSTRAINT fk_category_parent FOREIGN KEY (parent_no) REFERENCES book_category(category_no)
) ENGINE=InnoDB;

CREATE TABLE publisher (
  publisher_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  publisher_name VARCHAR(150) NOT NULL UNIQUE,
  address VARCHAR(255),
  phone VARCHAR(30)
) ENGINE=InnoDB;

CREATE TABLE author (
  author_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  author_name VARCHAR(100) NOT NULL,
  nationality VARCHAR(80),
  biography TEXT,
  UNIQUE KEY uk_author (author_name, nationality)
) ENGINE=InnoDB;

CREATE TABLE book (
  book_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  isbn VARCHAR(20) NOT NULL UNIQUE,
  title VARCHAR(200) NOT NULL,
  category_no BIGINT UNSIGNED NOT NULL,
  publisher_no BIGINT UNSIGNED NULL,
  publish_date DATE,
  edition VARCHAR(50),
  price DECIMAL(10,2),
  language VARCHAR(50) DEFAULT 'Chinese',
  summary TEXT,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_book_category FOREIGN KEY (category_no) REFERENCES book_category(category_no),
  CONSTRAINT fk_book_publisher FOREIGN KEY (publisher_no) REFERENCES publisher(publisher_no)
) ENGINE=InnoDB;

CREATE TABLE book_author (
  book_no BIGINT UNSIGNED NOT NULL,
  author_no BIGINT UNSIGNED NOT NULL,
  author_order INT UNSIGNED NOT NULL DEFAULT 1,
  PRIMARY KEY (book_no, author_no),
  CONSTRAINT fk_book_author_book FOREIGN KEY (book_no) REFERENCES book(book_no) ON DELETE CASCADE,
  CONSTRAINT fk_book_author_author FOREIGN KEY (author_no) REFERENCES author(author_no)
) ENGINE=InnoDB;

CREATE TABLE book_copy (
  copy_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  book_no BIGINT UNSIGNED NOT NULL,
  barcode VARCHAR(50) NOT NULL UNIQUE,
  location VARCHAR(100) NOT NULL,
  status ENUM('available', 'borrowed', 'maintenance', 'lost', 'removed') NOT NULL DEFAULT 'available',
  purchase_date DATE DEFAULT (CURRENT_DATE),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_copy_book FOREIGN KEY (book_no) REFERENCES book(book_no)
) ENGINE=InnoDB;

CREATE TABLE borrow_rule (
  rule_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  student_type ENUM('undergraduate') NOT NULL UNIQUE,
  max_borrow_count INT UNSIGNED NOT NULL,
  borrow_days INT UNSIGNED NOT NULL,
  max_renew_count INT UNSIGNED NOT NULL DEFAULT 1,
  fine_per_day DECIMAL(8,2) NOT NULL DEFAULT 0.50
) ENGINE=InnoDB;

CREATE TABLE business_sequence (
  business_type ENUM('borrow', 'reservation', 'overdue') NOT NULL,
  business_date DATE NOT NULL,
  current_value INT UNSIGNED NOT NULL,
  PRIMARY KEY (business_type, business_date)
) ENGINE=InnoDB;

CREATE TABLE borrow_record (
  borrow_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  borrow_code VARCHAR(24) NOT NULL UNIQUE,
  student_no BIGINT UNSIGNED NOT NULL,
  copy_no BIGINT UNSIGNED NOT NULL,
  borrow_librarian_no BIGINT UNSIGNED,
  return_librarian_no BIGINT UNSIGNED,
  borrow_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  due_time DATETIME NOT NULL,
  return_time DATETIME,
  renew_count INT UNSIGNED NOT NULL DEFAULT 0,
  status ENUM('borrowed', 'returned', 'overdue', 'lost') NOT NULL DEFAULT 'borrowed',
  CONSTRAINT fk_borrow_student FOREIGN KEY (student_no) REFERENCES student(student_no),
  CONSTRAINT fk_borrow_copy FOREIGN KEY (copy_no) REFERENCES book_copy(copy_no),
  CONSTRAINT fk_borrow_librarian FOREIGN KEY (borrow_librarian_no) REFERENCES librarian(librarian_no),
  CONSTRAINT fk_return_librarian FOREIGN KEY (return_librarian_no) REFERENCES librarian(librarian_no),
  INDEX idx_borrow_student_status (student_no, status),
  INDEX idx_borrow_copy_status (copy_no, status)
) ENGINE=InnoDB;

CREATE TABLE reservation (
  reservation_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  reservation_code VARCHAR(24) NOT NULL UNIQUE,
  student_no BIGINT UNSIGNED NOT NULL,
  book_no BIGINT UNSIGNED NOT NULL,
  reserved_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  borrow_date DATE,
  expire_at DATETIME,
  status ENUM('waiting', 'notified', 'fulfilled', 'cancelled', 'expired') NOT NULL DEFAULT 'waiting',
  handled_by_no BIGINT UNSIGNED,
  handled_at DATETIME,
  CONSTRAINT fk_reservation_student FOREIGN KEY (student_no) REFERENCES student(student_no),
  CONSTRAINT fk_reservation_book FOREIGN KEY (book_no) REFERENCES book(book_no),
  CONSTRAINT fk_reservation_librarian FOREIGN KEY (handled_by_no) REFERENCES librarian(librarian_no),
  INDEX idx_reservation_status (book_no, status, reserved_at)
) ENGINE=InnoDB;

CREATE TABLE overdue_record (
  overdue_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  overdue_code VARCHAR(24) NOT NULL UNIQUE,
  borrow_no BIGINT UNSIGNED NOT NULL UNIQUE,
  overdue_days INT UNSIGNED NOT NULL,
  fine_amount DECIMAL(10,2) NOT NULL,
  paid_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  status ENUM('unpaid', 'partial_paid', 'paid', 'waived') NOT NULL DEFAULT 'unpaid',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  paid_at DATETIME,
  CONSTRAINT fk_overdue_borrow FOREIGN KEY (borrow_no) REFERENCES borrow_record(borrow_no)
) ENGINE=InnoDB;

CREATE TABLE book_media (
  media_no BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  book_no BIGINT UNSIGNED NOT NULL,
  media_type ENUM('image', 'video', 'file') NOT NULL,
  title VARCHAR(150) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  mime_type VARCHAR(100),
  file_size BIGINT UNSIGNED,
  uploaded_by_no BIGINT UNSIGNED,
  uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_media_book FOREIGN KEY (book_no) REFERENCES book(book_no) ON DELETE CASCADE,
  CONSTRAINT fk_media_librarian FOREIGN KEY (uploaded_by_no) REFERENCES librarian(librarian_no)
) ENGINE=InnoDB;
