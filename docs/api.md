# API 接口说明

后端 Flask 提供 `/api` JSON 接口，前端 Vue 通过 HTTP + JSON 调用。所有需要登录的接口依赖 Flask Session Cookie。

统一返回格式：

```json
{
  "ok": true
}
```

错误返回格式：

```json
{
  "ok": false,
  "message": "错误信息"
}
```

## 认证接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/me` | 获取当前登录用户 |
| POST | `/api/login` | 登录 |
| POST | `/api/register/student` | 学生自助注册 |
| POST | `/api/logout` | 退出登录 |

`POST /api/login` 请求体：

```json
{
  "role": "student",
  "login": "pb22000001",
  "password": "123456"
}
```

`role` 可取：

- `student`
- `librarian`

`POST /api/register/student` 请求体：

```json
{
  "student_id": "pb22000002",
  "password": "123456",
  "confirm_password": "123456"
}
```

注册成功后，后端会直接写入登录 Session，并返回当前学生用户信息。姓名、学院、专业、电话、邮箱等信息在个人信息页面补充。密码至少 6 位，且只能包含数字或字母。

借阅和预约列表显示数据库生成的业务长编码：

```text
借阅编码：BR202606040001
预约编码：RV202606040001
违期编码：OD202606040001
```

自增主键仍作为内部关联键，业务长编码用于页面展示和记录查询。

## 公共接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/books?q=关键词&page=1&page_size=10` | 分页图书检索 |

## 学生端接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/student/dashboard` | 学生首页统计和借阅排行 |
| GET | `/api/student/borrows?page=1&page_size=10` | 分页查询我的借阅 |
| POST | `/api/student/borrows` | 学生端借出；无可借馆藏时加入预约队列 |
| POST | `/api/student/borrows/renew` | 延期本人未逾期的借阅 |
| POST | `/api/student/borrows/return` | 归还本人当前借阅 |
| GET | `/api/student/reservations?page=1&page_size=10` | 分页查询我的预约 |
| POST | `/api/student/reservations` | 提交预约 |
| PUT | `/api/student/reservations` | 修改本人有效预约的计划借出日期 |
| DELETE | `/api/student/reservations` | 取消本人有效预约 |
| GET | `/api/student/overdue` | 我的违期记录 |
| GET | `/api/student/profile` | 获取个人信息 |
| POST | `/api/student/profile` | 修改个人信息 |
| POST | `/api/student/password` | 修改密码 |

`POST /api/student/reservations` 请求体：

```json
{
  "book_no": 1,
  "borrow_date": "2026-06-10"
}
```

`borrow_date` 为学生选择的计划借出日期，必须晚于当天。

`PUT /api/student/reservations` 请求体：

```json
{
  "reservation_no": 1,
  "borrow_date": "2026-06-15"
}
```

只能修改本人状态为“待处理”或“已通知”的预约。数据库会同步更新预约过期时间。

`POST /api/student/borrows` 请求体：

```json
{
  "book_no": 1
}
```

若该书有可借副本，系统会立即借出；若当前无可借副本，系统会自动生成一条等待状态的预约队列记录。

`POST /api/student/borrows/renew` 和 `POST /api/student/borrows/return` 请求体：

```json
{
  "borrow_no": 1
}
```

延期次数和延期天数由 `borrow_rule` 表控制。延期与还书均通过数据库存储过程完成，并校验借阅记录属于当前登录学生。

`DELETE /api/student/reservations` 请求体：

```json
{
  "reservation_no": 1
}
```

只能取消本人状态为“待处理”或“已通知”的预约。

`POST /api/student/profile` 请求体：

```json
{
  "gender": "other",
  "college": "计算机科学与技术学院",
  "major": "计算机科学与技术",
  "phone": "13800000000",
  "email": "student@example.com"
}
```

姓名、学号、学生状态不允许学生自行修改。首次补全个人信息时姓名必填；电话和邮箱至少填写一项。电话需要填写 11 位手机号或座机号，邮箱需要符合常见邮箱格式。

`POST /api/student/password` 请求体：

```json
{
  "old_password": "123456",
  "new_password": "654321",
  "confirm_password": "654321"
}
```

新密码至少 6 位，且只能包含数字或字母。

## 管理员端接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/admin/dashboard` | 管理员首页统计和借阅排行 |
| GET | `/api/admin/books` | 图书、分类、出版社数据 |
| GET | `/api/admin/books/<book_no>` | 管理员图书详情，包含该书全部历史借阅记录 |
| POST | `/api/admin/books` | 新增图书、副本或媒体资料 |
| GET | `/api/admin/students?page=1&page_size=10` | 分页学生列表，可按学号和姓名查询 |
| GET | `/api/admin/students/<student_id>` | 学生详情及该学生全部历史借阅记录 |
| POST | `/api/admin/students` | 新增学生 |
| DELETE | `/api/admin/students` | 删除学生 |
| GET | `/api/admin/librarians?page=1&page_size=10` | 分页管理员列表，可按工号和姓名查询 |
| POST | `/api/admin/librarians` | 新增管理员 |
| DELETE | `/api/admin/librarians` | 删除或停用管理员 |
| GET | `/api/admin/borrow?page=1&page_size=10` | 分页可借/馆藏副本列表 |
| POST | `/api/admin/borrow` | 办理借书 |
| GET | `/api/admin/return?page=1&page_size=10&q=关键词` | 分页查询当前借出列表 |
| POST | `/api/admin/return` | 办理还书 |
| GET | `/api/admin/reservations?page=1&page_size=10` | 分页预约列表 |
| POST | `/api/admin/reservations` | 更新预约状态 |
| GET | `/api/admin/overdue` | 违期列表 |
| POST | `/api/admin/overdue` | 登记罚金缴清 |

`GET /api/admin/students` 查询参数：

```text
student_id=学号关键字
name=姓名关键字
```

`POST /api/admin/students` 请求体：

```json
{
  "student_id": "pb22000002"
}
```

`DELETE /api/admin/students` 请求体：

```json
{
  "student_id": "pb22000002"
}
```

如果学生已有借阅或预约记录，系统不会直接删除该学生。

`POST /api/admin/librarians` 请求体：

```json
{
  "employee_id": "lib001",
  "name": "新管理员",
  "password": "123456",
  "phone": "0551-00000000",
  "email": "lib@example.com",
  "position": "流通管理员"
}
```

管理员账号不开放公开注册，只能由已登录管理员新增。自定义初始密码至少 6 位，且只能包含数字或字母。

`DELETE /api/admin/librarians` 请求体：

```json
{
  "employee_id": "lib001"
}
```

不能删除当前登录的管理员账号。如果管理员已有借书、还书、预约处理或附件上传记录，系统会停用账号而不是物理删除。

`GET /api/admin/librarians` 查询参数：

```text
employee_id=工号关键字
name=姓名关键字
```

`POST /api/admin/books` 新增图书：

```json
{
  "action": "book",
  "isbn": "9787300000003",
  "title": "数据库实验指导",
  "category_no": 1,
  "publisher_no": 1,
  "publish_date": "2026-01-01",
  "edition": "第1版",
  "price": "39.00",
  "language": "Chinese",
  "summary": "课程实验用书"
}
```

`POST /api/admin/books` 新增馆藏副本：

```json
{
  "action": "copy",
  "book_no": 1,
  "barcode": "BC000010",
  "location": "一楼A区",
  "purchase_date": "2026-06-01"
}
```

`POST /api/admin/books` 修改图书简介：

```json
{
  "action": "summary",
  "book_no": 1,
  "summary": "修改后的图书简介"
}
```

简介修改通过数据库存储过程完成。空简介会在数据库中保存为 `NULL`。

`POST /api/admin/books` 上传图书附件，使用 `multipart/form-data`，字段为：

```text
action=media
book_no=1
file=<本地文件>
```

上传文件最大为 50 MB，文件保存在 `uploads/books/图书编号/`，数据库保存相对路径和元数据。

`POST /api/admin/borrow` 请求体：

```json
{
  "student_id": "pb22000001",
  "barcode": "BC000001"
}
```

`POST /api/admin/return` 请求体：

```json
{
  "borrow_no": 1
}
```

`POST /api/admin/reservations` 请求体：

```json
{
  "reservation_no": 1,
  "status": "notified"
}
```

`status` 提交时使用枚举值，界面显示为中文：

| 提交值 | 页面显示 |
|---|---|
| `notified` | 已通知 |
| `fulfilled` | 已完成 |
| `cancelled` | 已取消 |
| `expired` | 已过期 |

## 后端接口文件对应关系

| 文件 | 作用 |
|---|---|
| `backend/routes/auth.py` | 登录、注册、退出、当前用户 |
| `backend/routes/student.py` | 学生端 API |
| `backend/routes/admin_dashboard.py` | 管理员首页统计 |
| `backend/routes/admin_books.py` | 管理员图书、副本、附件接口 |
| `backend/routes/admin_users.py` | 管理员学生和管理员账号接口 |
| `backend/routes/admin_circulation.py` | 管理员借书、还书、预约、违期接口 |
| `backend/routes/helpers.py` | 登录态、鉴权、响应工具 |
