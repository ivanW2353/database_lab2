USE db_lab2;

DROP TRIGGER IF EXISTS trg_student_before_insert;
DROP TRIGGER IF EXISTS trg_student_before_update;
DROP TRIGGER IF EXISTS trg_borrow_before_insert;
DROP TRIGGER IF EXISTS trg_borrow_after_insert;
DROP TRIGGER IF EXISTS trg_borrow_after_update;
DROP TRIGGER IF EXISTS trg_reservation_before_insert;
DROP TRIGGER IF EXISTS trg_overdue_before_insert;
DROP PROCEDURE IF EXISTS sp_borrow_book;
DROP PROCEDURE IF EXISTS sp_return_book;
DROP PROCEDURE IF EXISTS sp_renew_borrow;
DROP PROCEDURE IF EXISTS sp_update_reservation_date;
DROP PROCEDURE IF EXISTS sp_update_book_summary;
DROP FUNCTION IF EXISTS fn_overdue_days;
DROP FUNCTION IF EXISTS fn_overdue_fine;

DELIMITER //

CREATE FUNCTION fn_overdue_days(p_due_time DATETIME, p_return_time DATETIME)
RETURNS INT
DETERMINISTIC
BEGIN
  DECLARE v_days INT;
  SET v_days = TIMESTAMPDIFF(DAY, p_due_time, COALESCE(p_return_time, NOW()));
  RETURN IF(v_days > 0, v_days, 0);
END//

CREATE FUNCTION fn_overdue_fine(p_days INT, p_fine_per_day DECIMAL(8,2))
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
  RETURN IF(p_days > 0, p_days * p_fine_per_day, 0.00);
END//

CREATE TRIGGER trg_student_before_insert
BEFORE INSERT ON student
FOR EACH ROW
BEGIN
  IF NOT (UPPER(NEW.student_id) REGEXP '^(PB|JL|XK|XJ|NS|PL)[0-9]{8}$') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid USTC undergraduate student id';
  END IF;
END//

CREATE TRIGGER trg_student_before_update
BEFORE UPDATE ON student
FOR EACH ROW
BEGIN
  IF NOT (UPPER(NEW.student_id) REGEXP '^(PB|JL|XK|XJ|NS|PL)[0-9]{8}$') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid USTC undergraduate student id';
  END IF;
END//

CREATE TRIGGER trg_borrow_before_insert
BEFORE INSERT ON borrow_record
FOR EACH ROW
BEGIN
  DECLARE v_status VARCHAR(20);
  DECLARE v_sequence INT UNSIGNED;
  SELECT status INTO v_status FROM book_copy WHERE copy_no = NEW.copy_no;
  IF v_status <> 'available' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book copy is not available';
  END IF;
  INSERT INTO business_sequence (business_type, business_date, current_value)
  VALUES ('borrow', CURDATE(), LAST_INSERT_ID(1))
  ON DUPLICATE KEY UPDATE current_value = LAST_INSERT_ID(current_value + 1);
  SET v_sequence = LAST_INSERT_ID();
  SET NEW.borrow_code = CONCAT('BR', DATE_FORMAT(CURDATE(), '%Y%m%d'), LPAD(v_sequence, 4, '0'));
END//

CREATE TRIGGER trg_reservation_before_insert
BEFORE INSERT ON reservation
FOR EACH ROW
BEGIN
  DECLARE v_sequence INT UNSIGNED;
  INSERT INTO business_sequence (business_type, business_date, current_value)
  VALUES ('reservation', CURDATE(), LAST_INSERT_ID(1))
  ON DUPLICATE KEY UPDATE current_value = LAST_INSERT_ID(current_value + 1);
  SET v_sequence = LAST_INSERT_ID();
  SET NEW.reservation_code = CONCAT('RV', DATE_FORMAT(CURDATE(), '%Y%m%d'), LPAD(v_sequence, 4, '0'));
END//

CREATE TRIGGER trg_overdue_before_insert
BEFORE INSERT ON overdue_record
FOR EACH ROW
BEGIN
  DECLARE v_sequence INT UNSIGNED;
  INSERT INTO business_sequence (business_type, business_date, current_value)
  VALUES ('overdue', CURDATE(), LAST_INSERT_ID(1))
  ON DUPLICATE KEY UPDATE current_value = LAST_INSERT_ID(current_value + 1);
  SET v_sequence = LAST_INSERT_ID();
  SET NEW.overdue_code = CONCAT('OD', DATE_FORMAT(CURDATE(), '%Y%m%d'), LPAD(v_sequence, 4, '0'));
END//

CREATE TRIGGER trg_borrow_after_insert
AFTER INSERT ON borrow_record
FOR EACH ROW
BEGIN
  UPDATE book_copy SET status = 'borrowed' WHERE copy_no = NEW.copy_no;
END//

CREATE TRIGGER trg_borrow_after_update
AFTER UPDATE ON borrow_record
FOR EACH ROW
BEGIN
  IF NEW.status = 'returned' AND OLD.status <> 'returned' THEN
    UPDATE book_copy SET status = 'available' WHERE copy_no = NEW.copy_no;
  ELSEIF NEW.status = 'lost' AND OLD.status <> 'lost' THEN
    UPDATE book_copy SET status = 'lost' WHERE copy_no = NEW.copy_no;
  END IF;
END//

CREATE PROCEDURE sp_borrow_book(
  IN p_student_no BIGINT UNSIGNED,
  IN p_copy_no BIGINT UNSIGNED,
  IN p_librarian_no BIGINT UNSIGNED
)
BEGIN
  DECLARE v_student_type ENUM('undergraduate');
  DECLARE v_max_count INT UNSIGNED;
  DECLARE v_borrow_days INT UNSIGNED;
  DECLARE v_current_count INT UNSIGNED;
  DECLARE v_unpaid_count INT UNSIGNED;
  DECLARE v_status VARCHAR(20);

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;

  SELECT student_type INTO v_student_type
  FROM student
  WHERE student_no = p_student_no AND status = 'normal'
  FOR UPDATE;

  SELECT max_borrow_count, borrow_days INTO v_max_count, v_borrow_days
  FROM borrow_rule
  WHERE student_type = v_student_type;

  SELECT COUNT(*) INTO v_current_count
  FROM borrow_record
  WHERE student_no = p_student_no AND status IN ('borrowed', 'overdue');

  SELECT COUNT(*) INTO v_unpaid_count
  FROM overdue_record o
  JOIN borrow_record b ON b.borrow_no = o.borrow_no
  WHERE b.student_no = p_student_no AND o.status IN ('unpaid', 'partial_paid');

  SELECT status INTO v_status
  FROM book_copy
  WHERE copy_no = p_copy_no
  FOR UPDATE;

  IF v_status <> 'available' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book copy is not available';
  ELSEIF v_current_count >= v_max_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Borrow limit exceeded';
  ELSEIF v_unpaid_count > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student has unpaid overdue fine';
  ELSE
    INSERT INTO borrow_record (student_no, copy_no, borrow_librarian_no, due_time)
    VALUES (p_student_no, p_copy_no, p_librarian_no, DATE_ADD(NOW(), INTERVAL v_borrow_days DAY));
  END IF;

  COMMIT;
END//

CREATE PROCEDURE sp_return_book(
  IN p_borrow_no BIGINT UNSIGNED,
  IN p_librarian_no BIGINT UNSIGNED,
  IN p_student_no BIGINT UNSIGNED
)
BEGIN
  DECLARE v_due_time DATETIME;
  DECLARE v_return_time DATETIME;
  DECLARE v_days INT;
  DECLARE v_fine_per_day DECIMAL(8,2);
  DECLARE v_student_type ENUM('undergraduate');
  DECLARE v_record_count INT UNSIGNED;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;
  SET v_return_time = NOW();

  SELECT COUNT(*) INTO v_record_count
  FROM borrow_record
  WHERE borrow_no = p_borrow_no
    AND status IN ('borrowed', 'overdue')
    AND (p_student_no IS NULL OR student_no = p_student_no);

  IF v_record_count = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Borrow record is not active or does not belong to student';
  END IF;

  SELECT b.due_time, s.student_type
  INTO v_due_time, v_student_type
  FROM borrow_record b
  JOIN student s ON s.student_no = b.student_no
  WHERE b.borrow_no = p_borrow_no
    AND b.status IN ('borrowed', 'overdue')
    AND (p_student_no IS NULL OR b.student_no = p_student_no)
  FOR UPDATE;

  UPDATE borrow_record
  SET return_time = v_return_time,
      return_librarian_no = p_librarian_no,
      status = 'returned'
  WHERE borrow_no = p_borrow_no;

  SET v_days = fn_overdue_days(v_due_time, v_return_time);

  IF v_days > 0 THEN
    SELECT fine_per_day INTO v_fine_per_day
    FROM borrow_rule
    WHERE student_type = v_student_type;

    INSERT INTO overdue_record (borrow_no, overdue_days, fine_amount)
    VALUES (p_borrow_no, v_days, fn_overdue_fine(v_days, v_fine_per_day))
    ON DUPLICATE KEY UPDATE
      overdue_days = VALUES(overdue_days),
      fine_amount = VALUES(fine_amount);
  END IF;

  COMMIT;
END//

CREATE PROCEDURE sp_renew_borrow(
  IN p_borrow_no BIGINT UNSIGNED,
  IN p_student_no BIGINT UNSIGNED
)
BEGIN
  DECLARE v_student_type ENUM('undergraduate');
  DECLARE v_status VARCHAR(20);
  DECLARE v_due_time DATETIME;
  DECLARE v_renew_count INT UNSIGNED;
  DECLARE v_max_renew_count INT UNSIGNED;
  DECLARE v_borrow_days INT UNSIGNED;
  DECLARE v_unpaid_count INT UNSIGNED;
  DECLARE v_record_count INT UNSIGNED;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;

  SELECT COUNT(*) INTO v_record_count
  FROM borrow_record
  WHERE borrow_no = p_borrow_no AND student_no = p_student_no;

  IF v_record_count = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Borrow record does not belong to student';
  END IF;

  SELECT b.status, b.due_time, b.renew_count, s.student_type
  INTO v_status, v_due_time, v_renew_count, v_student_type
  FROM borrow_record b
  JOIN student s ON s.student_no = b.student_no
  WHERE b.borrow_no = p_borrow_no AND b.student_no = p_student_no
  FOR UPDATE;

  SELECT max_renew_count, borrow_days
  INTO v_max_renew_count, v_borrow_days
  FROM borrow_rule
  WHERE student_type = v_student_type;

  SELECT COUNT(*) INTO v_unpaid_count
  FROM overdue_record o
  JOIN borrow_record b ON b.borrow_no = o.borrow_no
  WHERE b.student_no = p_student_no AND o.status IN ('unpaid', 'partial_paid');

  IF v_status <> 'borrowed' OR v_due_time < NOW() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only active non-overdue borrow can be renewed';
  ELSEIF v_renew_count >= v_max_renew_count THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Renew limit exceeded';
  ELSEIF v_unpaid_count > 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Student has unpaid overdue fine';
  ELSE
    UPDATE borrow_record
    SET due_time = DATE_ADD(due_time, INTERVAL v_borrow_days DAY),
        renew_count = renew_count + 1
    WHERE borrow_no = p_borrow_no;
  END IF;

  COMMIT;
END//

CREATE PROCEDURE sp_update_reservation_date(
  IN p_reservation_no BIGINT UNSIGNED,
  IN p_student_no BIGINT UNSIGNED,
  IN p_borrow_date DATE
)
BEGIN
  DECLARE v_status VARCHAR(20);
  DECLARE v_record_count INT UNSIGNED;

  DECLARE EXIT HANDLER FOR SQLEXCEPTION
  BEGIN
    ROLLBACK;
    RESIGNAL;
  END;

  START TRANSACTION;

  SELECT COUNT(*) INTO v_record_count
  FROM reservation
  WHERE reservation_no = p_reservation_no AND student_no = p_student_no;

  IF v_record_count = 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation does not belong to student';
  END IF;

  SELECT status INTO v_status
  FROM reservation
  WHERE reservation_no = p_reservation_no AND student_no = p_student_no
  FOR UPDATE;

  IF v_status NOT IN ('waiting', 'notified') THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation status does not allow date update';
  ELSEIF p_borrow_date IS NULL OR p_borrow_date <= CURDATE() THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation borrow date must be later than today';
  ELSE
    UPDATE reservation
    SET borrow_date = p_borrow_date,
        expire_at = DATE_ADD(p_borrow_date, INTERVAL 1 DAY)
    WHERE reservation_no = p_reservation_no;
  END IF;

  COMMIT;
END//

CREATE PROCEDURE sp_update_book_summary(
  IN p_book_no BIGINT UNSIGNED,
  IN p_summary TEXT
)
BEGIN
  DECLARE v_record_count INT UNSIGNED;

  START TRANSACTION;

  SELECT COUNT(*) INTO v_record_count
  FROM book
  WHERE book_no = p_book_no;

  IF v_record_count = 0 THEN
    ROLLBACK;
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book does not exist';
  ELSE
    UPDATE book
    SET summary = NULLIF(TRIM(p_summary), '')
    WHERE book_no = p_book_no;
    COMMIT;
  END IF;
END//

DELIMITER ;
