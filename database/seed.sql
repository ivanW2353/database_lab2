USE db_lab2;

INSERT INTO borrow_rule (student_type, max_borrow_count, borrow_days, max_renew_count, fine_per_day) VALUES
  ('undergraduate', 5, 30, 1, 0.50);

INSERT INTO book_category (category_code, category_name) VALUES
  ('A', '马列主义、毛泽东思想、邓小平理论'),
  ('B', '哲学、宗教'),
  ('C', '社会科学总论'),
  ('D', '政治、法律'),
  ('E', '军事'),
  ('F', '经济'),
  ('G', '文化、科学、教育、体育'),
  ('H', '语言、文字'),
  ('I', '文学'),
  ('J', '艺术'),
  ('K', '历史、地理'),
  ('N', '自然科学总论'),
  ('O', '数理科学与化学'),
  ('P', '天文学、地球科学'),
  ('Q', '生物科学'),
  ('R', '医药、卫生'),
  ('S', '农业科学'),
  ('T', '工业技术'),
  ('U', '交通运输'),
  ('V', '航空、航天'),
  ('X', '环境科学,安全科学'),
  ('Z', '综合性图书');

INSERT INTO book_category (parent_no, category_code, category_name)
SELECT category_no, 'TP', '自动化技术、计算机技术'
FROM book_category
WHERE category_code = 'T';

INSERT INTO publisher (publisher_name, address, phone) VALUES
  ('清华大学出版社', '北京', '010-00000000'),
  ('中国科学技术大学出版社', '合肥', '0551-00000000');

INSERT INTO author (author_name, nationality, biography) VALUES
  ('数据库课程组', '中国', '数据库系统及应用课程演示作者'),
  ('图书馆技术部', '中国', '图书馆信息化资料维护团队');

INSERT INTO book (isbn, title, category_no, publisher_no, publish_date, edition, price, language, summary) VALUES
  ('9787300000001', '数据库系统概论', (SELECT category_no FROM book_category WHERE category_code='TP'), 1, '2024-01-01', '第1版', 59.00, 'Chinese', '数据库课程设计参考书'),
  ('9787312000002', '图书馆信息管理实践', (SELECT category_no FROM book_category WHERE category_code='TP'), 2, '2025-03-01', '第1版', 45.00, 'Chinese', '图书管理系统设计与实现参考资料');

INSERT INTO book_author (book_no, author_no, author_order) VALUES
  (1, 1, 1),
  (2, 2, 1);

INSERT INTO book_copy (book_no, barcode, location, status, purchase_date) VALUES
  (1, 'BC000001', '一楼A区-01', 'available', '2024-02-01'),
  (1, 'BC000002', '一楼A区-02', 'available', '2024-02-01'),
  (2, 'BC000003', '二楼B区-01', 'available', '2025-04-01');
