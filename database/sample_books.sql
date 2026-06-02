USE db_lab2;

INSERT IGNORE INTO author (author_name, nationality, biography) VALUES
  ('图书分类示例编写组', '中国', '用于课程设计演示的中图法分类示例作者');

INSERT IGNORE INTO book (isbn, title, category_no, publisher_no, publish_date, edition, price, language, summary) VALUES
  ('9787001000001', '马列主义经典著作导读', (SELECT category_no FROM book_category WHERE category_code='A'), 1, '2026-01-01', '第1版', 36.00, 'Chinese', '中图法示例书目：A类'),
  ('9787001000002', '毛泽东思想概论', (SELECT category_no FROM book_category WHERE category_code='A'), 1, '2026-01-01', '第1版', 38.00, 'Chinese', '中图法示例书目：A类'),
  ('9787001000003', '邓小平理论学习纲要', (SELECT category_no FROM book_category WHERE category_code='A'), 1, '2026-01-01', '第1版', 35.00, 'Chinese', '中图法示例书目：A类'),
  ('9787002000001', '中国哲学简史', (SELECT category_no FROM book_category WHERE category_code='B'), 1, '2026-01-01', '第1版', 42.00, 'Chinese', '中图法示例书目：B类'),
  ('9787002000002', '西方哲学导论', (SELECT category_no FROM book_category WHERE category_code='B'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：B类'),
  ('9787002000003', '宗教学基础', (SELECT category_no FROM book_category WHERE category_code='B'), 1, '2026-01-01', '第1版', 39.00, 'Chinese', '中图法示例书目：B类'),
  ('9787003000001', '社会科学研究方法', (SELECT category_no FROM book_category WHERE category_code='C'), 1, '2026-01-01', '第1版', 49.00, 'Chinese', '中图法示例书目：C类'),
  ('9787003000002', '统计学与社会调查', (SELECT category_no FROM book_category WHERE category_code='C'), 1, '2026-01-01', '第1版', 45.00, 'Chinese', '中图法示例书目：C类'),
  ('9787003000003', '公共管理概论', (SELECT category_no FROM book_category WHERE category_code='C'), 1, '2026-01-01', '第1版', 43.00, 'Chinese', '中图法示例书目：C类'),
  ('9787004000001', '政治学原理', (SELECT category_no FROM book_category WHERE category_code='D'), 1, '2026-01-01', '第1版', 41.00, 'Chinese', '中图法示例书目：D类'),
  ('9787004000002', '法学导论', (SELECT category_no FROM book_category WHERE category_code='D'), 1, '2026-01-01', '第1版', 47.00, 'Chinese', '中图法示例书目：D类'),
  ('9787004000003', '宪法学基础', (SELECT category_no FROM book_category WHERE category_code='D'), 1, '2026-01-01', '第1版', 44.00, 'Chinese', '中图法示例书目：D类'),
  ('9787005000001', '军事理论教程', (SELECT category_no FROM book_category WHERE category_code='E'), 1, '2026-01-01', '第1版', 32.00, 'Chinese', '中图法示例书目：E类'),
  ('9787005000002', '国防教育概论', (SELECT category_no FROM book_category WHERE category_code='E'), 1, '2026-01-01', '第1版', 34.00, 'Chinese', '中图法示例书目：E类'),
  ('9787005000003', '现代战略学基础', (SELECT category_no FROM book_category WHERE category_code='E'), 1, '2026-01-01', '第1版', 39.00, 'Chinese', '中图法示例书目：E类'),
  ('9787006000001', '微观经济学', (SELECT category_no FROM book_category WHERE category_code='F'), 1, '2026-01-01', '第1版', 52.00, 'Chinese', '中图法示例书目：F类'),
  ('9787006000002', '宏观经济学', (SELECT category_no FROM book_category WHERE category_code='F'), 1, '2026-01-01', '第1版', 52.00, 'Chinese', '中图法示例书目：F类'),
  ('9787006000003', '会计学原理', (SELECT category_no FROM book_category WHERE category_code='F'), 1, '2026-01-01', '第1版', 48.00, 'Chinese', '中图法示例书目：F类'),
  ('9787007000001', '教育学基础', (SELECT category_no FROM book_category WHERE category_code='G'), 1, '2026-01-01', '第1版', 40.00, 'Chinese', '中图法示例书目：G类'),
  ('9787007000002', '图书馆学概论', (SELECT category_no FROM book_category WHERE category_code='G'), 1, '2026-01-01', '第1版', 45.00, 'Chinese', '中图法示例书目：G类'),
  ('9787007000003', '体育科学导论', (SELECT category_no FROM book_category WHERE category_code='G'), 1, '2026-01-01', '第1版', 37.00, 'Chinese', '中图法示例书目：G类'),
  ('9787008000001', '现代汉语', (SELECT category_no FROM book_category WHERE category_code='H'), 1, '2026-01-01', '第1版', 42.00, 'Chinese', '中图法示例书目：H类'),
  ('9787008000002', '大学英语阅读', (SELECT category_no FROM book_category WHERE category_code='H'), 1, '2026-01-01', '第1版', 39.00, 'Chinese', '中图法示例书目：H类'),
  ('9787008000003', '语言学概论', (SELECT category_no FROM book_category WHERE category_code='H'), 1, '2026-01-01', '第1版', 43.00, 'Chinese', '中图法示例书目：H类'),
  ('9787009000001', '中国古代文学选读', (SELECT category_no FROM book_category WHERE category_code='I'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：I类'),
  ('9787009000002', '中国现当代文学', (SELECT category_no FROM book_category WHERE category_code='I'), 1, '2026-01-01', '第1版', 44.00, 'Chinese', '中图法示例书目：I类'),
  ('9787009000003', '外国文学名著导读', (SELECT category_no FROM book_category WHERE category_code='I'), 1, '2026-01-01', '第1版', 48.00, 'Chinese', '中图法示例书目：I类'),
  ('9787010000001', '美术鉴赏', (SELECT category_no FROM book_category WHERE category_code='J'), 1, '2026-01-01', '第1版', 55.00, 'Chinese', '中图法示例书目：J类'),
  ('9787010000002', '音乐基础理论', (SELECT category_no FROM book_category WHERE category_code='J'), 1, '2026-01-01', '第1版', 41.00, 'Chinese', '中图法示例书目：J类'),
  ('9787010000003', '设计艺术概论', (SELECT category_no FROM book_category WHERE category_code='J'), 1, '2026-01-01', '第1版', 50.00, 'Chinese', '中图法示例书目：J类'),
  ('9787011000001', '中国通史', (SELECT category_no FROM book_category WHERE category_code='K'), 1, '2026-01-01', '第1版', 58.00, 'Chinese', '中图法示例书目：K类'),
  ('9787011000002', '世界历史导论', (SELECT category_no FROM book_category WHERE category_code='K'), 1, '2026-01-01', '第1版', 53.00, 'Chinese', '中图法示例书目：K类'),
  ('9787011000003', '中国地理概论', (SELECT category_no FROM book_category WHERE category_code='K'), 1, '2026-01-01', '第1版', 47.00, 'Chinese', '中图法示例书目：K类'),
  ('9787012000001', '自然科学概论', (SELECT category_no FROM book_category WHERE category_code='N'), 1, '2026-01-01', '第1版', 43.00, 'Chinese', '中图法示例书目：N类'),
  ('9787012000002', '科学技术史', (SELECT category_no FROM book_category WHERE category_code='N'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：N类'),
  ('9787012000003', '科学研究方法', (SELECT category_no FROM book_category WHERE category_code='N'), 1, '2026-01-01', '第1版', 42.00, 'Chinese', '中图法示例书目：N类'),
  ('9787013000001', '高等数学', (SELECT category_no FROM book_category WHERE category_code='O'), 1, '2026-01-01', '第1版', 49.00, 'Chinese', '中图法示例书目：O类'),
  ('9787013000002', '线性代数', (SELECT category_no FROM book_category WHERE category_code='O'), 1, '2026-01-01', '第1版', 36.00, 'Chinese', '中图法示例书目：O类'),
  ('9787013000003', '大学化学基础', (SELECT category_no FROM book_category WHERE category_code='O'), 1, '2026-01-01', '第1版', 44.00, 'Chinese', '中图法示例书目：O类'),
  ('9787014000001', '天文学导论', (SELECT category_no FROM book_category WHERE category_code='P'), 1, '2026-01-01', '第1版', 51.00, 'Chinese', '中图法示例书目：P类'),
  ('9787014000002', '地球科学概论', (SELECT category_no FROM book_category WHERE category_code='P'), 1, '2026-01-01', '第1版', 48.00, 'Chinese', '中图法示例书目：P类'),
  ('9787014000003', '气象学基础', (SELECT category_no FROM book_category WHERE category_code='P'), 1, '2026-01-01', '第1版', 45.00, 'Chinese', '中图法示例书目：P类'),
  ('9787015000001', '普通生物学', (SELECT category_no FROM book_category WHERE category_code='Q'), 1, '2026-01-01', '第1版', 50.00, 'Chinese', '中图法示例书目：Q类'),
  ('9787015000002', '细胞生物学', (SELECT category_no FROM book_category WHERE category_code='Q'), 1, '2026-01-01', '第1版', 54.00, 'Chinese', '中图法示例书目：Q类'),
  ('9787015000003', '生态学基础', (SELECT category_no FROM book_category WHERE category_code='Q'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：Q类'),
  ('9787016000001', '基础医学概论', (SELECT category_no FROM book_category WHERE category_code='R'), 1, '2026-01-01', '第1版', 58.00, 'Chinese', '中图法示例书目：R类'),
  ('9787016000002', '公共卫生导论', (SELECT category_no FROM book_category WHERE category_code='R'), 1, '2026-01-01', '第1版', 49.00, 'Chinese', '中图法示例书目：R类'),
  ('9787016000003', '药学基础', (SELECT category_no FROM book_category WHERE category_code='R'), 1, '2026-01-01', '第1版', 52.00, 'Chinese', '中图法示例书目：R类'),
  ('9787017000001', '农业科学概论', (SELECT category_no FROM book_category WHERE category_code='S'), 1, '2026-01-01', '第1版', 44.00, 'Chinese', '中图法示例书目：S类'),
  ('9787017000002', '作物栽培学', (SELECT category_no FROM book_category WHERE category_code='S'), 1, '2026-01-01', '第1版', 47.00, 'Chinese', '中图法示例书目：S类'),
  ('9787017000003', '园艺学基础', (SELECT category_no FROM book_category WHERE category_code='S'), 1, '2026-01-01', '第1版', 45.00, 'Chinese', '中图法示例书目：S类'),
  ('9787018000001', '机械工程基础', (SELECT category_no FROM book_category WHERE category_code='T'), 1, '2026-01-01', '第1版', 56.00, 'Chinese', '中图法示例书目：T类'),
  ('9787018000002', '电工电子技术', (SELECT category_no FROM book_category WHERE category_code='T'), 1, '2026-01-01', '第1版', 52.00, 'Chinese', '中图法示例书目：T类'),
  ('9787018000003', '工程制图', (SELECT category_no FROM book_category WHERE category_code='T'), 1, '2026-01-01', '第1版', 48.00, 'Chinese', '中图法示例书目：T类'),
  ('9787019000001', '交通运输工程导论', (SELECT category_no FROM book_category WHERE category_code='U'), 1, '2026-01-01', '第1版', 45.00, 'Chinese', '中图法示例书目：U类'),
  ('9787019000002', '道路工程基础', (SELECT category_no FROM book_category WHERE category_code='U'), 1, '2026-01-01', '第1版', 49.00, 'Chinese', '中图法示例书目：U类'),
  ('9787019000003', '铁路运输组织', (SELECT category_no FROM book_category WHERE category_code='U'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：U类'),
  ('9787020000001', '航空航天概论', (SELECT category_no FROM book_category WHERE category_code='V'), 1, '2026-01-01', '第1版', 55.00, 'Chinese', '中图法示例书目：V类'),
  ('9787020000002', '飞行器设计基础', (SELECT category_no FROM book_category WHERE category_code='V'), 1, '2026-01-01', '第1版', 59.00, 'Chinese', '中图法示例书目：V类'),
  ('9787020000003', '航天工程导论', (SELECT category_no FROM book_category WHERE category_code='V'), 1, '2026-01-01', '第1版', 57.00, 'Chinese', '中图法示例书目：V类'),
  ('9787021000001', '环境科学概论', (SELECT category_no FROM book_category WHERE category_code='X'), 1, '2026-01-01', '第1版', 48.00, 'Chinese', '中图法示例书目：X类'),
  ('9787021000002', '安全工程基础', (SELECT category_no FROM book_category WHERE category_code='X'), 1, '2026-01-01', '第1版', 46.00, 'Chinese', '中图法示例书目：X类'),
  ('9787021000003', '环境监测技术', (SELECT category_no FROM book_category WHERE category_code='X'), 1, '2026-01-01', '第1版', 50.00, 'Chinese', '中图法示例书目：X类'),
  ('9787022000001', '综合知识手册', (SELECT category_no FROM book_category WHERE category_code='Z'), 1, '2026-01-01', '第1版', 39.00, 'Chinese', '中图法示例书目：Z类'),
  ('9787022000002', '百科知识读本', (SELECT category_no FROM book_category WHERE category_code='Z'), 1, '2026-01-01', '第1版', 42.00, 'Chinese', '中图法示例书目：Z类'),
  ('9787022000003', '大学生通识读本', (SELECT category_no FROM book_category WHERE category_code='Z'), 1, '2026-01-01', '第1版', 40.00, 'Chinese', '中图法示例书目：Z类');

INSERT IGNORE INTO book_author (book_no, author_no, author_order)
SELECT b.book_no, a.author_no, 1
FROM book b
JOIN author a ON a.author_name = '图书分类示例编写组'
WHERE b.summary LIKE '中图法示例书目%';

INSERT IGNORE INTO book_copy (book_no, barcode, location, status, purchase_date)
SELECT b.book_no, CONCAT('CLC', LPAD(b.book_no, 6, '0')), CONCAT('中图法-', c.category_code, '区'), 'available', '2026-06-01'
FROM book b
JOIN book_category c ON c.category_no = b.category_no
WHERE b.summary LIKE '中图法示例书目%';
