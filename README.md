# 图书管理系统

本项目是数据库系统及应用课程设计，采用 B/S 架构实现图书管理系统。

系统使用 Vue 3 + Vite 实现前端界面，Flask 提供后端 API，MySQL 作为数据库。前端通过 HTTP + JSON 调用 Flask API。

## 技术栈

- 前端：Vue 3、Vite、Tabler
- 后端：Flask、SQLAlchemy、PyMySQL
- 数据库：MySQL 8
- 运行环境：Python 3、Node.js、npm

## 默认数据库配置

```text
数据库名：db_lab2
用户名：root
密码：123456
```

配置位置：

- `backend/config.py`
- `backend/extensions.py`

## 项目结构

```text
database_lab2/
├─ backend/                  # Flask 后端
│  ├─ app.py                 # Flask 启动入口
│  ├─ factory.py             # Flask 应用工厂
│  ├─ routes/                # API 接口
│  ├─ models/                # SQLAlchemy 模型
│  ├─ services/              # 业务逻辑
│  ├─ mysql_cli.py           # MySQL 命令行访问封装
│  ├─ security.py            # 密码哈希和校验
│  ├─ audit.py               # 业务审计日志
│  └─ config.py              # 后端配置
├─ frontend/                 # Vue 前端
├─ database/                 # 数据库脚本
├─ docs/                     # 需求分析、API、项目结构文档
├─ tests/                    # 后端单元测试
└─ requirements.txt          # Python 依赖
```

详细说明见：

```text
docs/项目结构.md
```

## 初始化

### 1. 安装 Python 依赖

```bash
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

如果没有虚拟环境，可以先创建：

```bash
python -m venv .venv
```

### 2. 初始化数据库

首先登录 MySQL：

```bash
mysql -uroot -p123456
```

进入 MySQL 后执行：

```SQL
source database/import_all.sql;
```

或

```SQL
\. database/import_all.sql
```

该命令会重建 `db_lab2` 数据库，并导入表结构、初始数据、触发器、函数和存储过程。

数据库脚本位于：

```text
database/
├─ schema.sql       # 表结构
├─ seed.sql         # 初始数据
├─ business.sql     # 触发器、函数、存储过程
└─ import_all.sql   # 一键导入脚本
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

## 启动系统

终端一：启动 Flask 后端：

```bash
.\.venv\Scripts\python.exe -B -m backend.app
```

终端二：启动 Vue 前端：

```bash
cd frontend
npm run dev
```

访问：

```text
http://127.0.0.1:5173
```

停止系统时，在两个终端中分别按 `Ctrl+C`。

## 默认账号

```text
学生账号：pb22000001
学生密码：123456

管理员账号：admin
管理员密码：123456
```

学生可以自行注册，也可以由管理员新增账号。学生自行注册成功后会直接登录，并进入单独界面补全个人信息。登录时使用学号和个人密码，不设置额外登录账号。学号前两位字母不强制大写，系统会按统一规则处理。

密码规则：至少 6 位，且只能包含数字或字母。

## 使用说明

学生和管理员的具体操作说明已分别整理为两个文件：

- `docs/学生使用说明.md`
- `docs/管理员使用说明.md`
- `docs/实验报告.md`

## 已实现功能

- 学生注册、登录、首次完善个人信息、个人信息维护、修改密码
- 图书检索、图书预约、借阅记录查询、预约记录查询、违期记录查询
- 学生自主借书、还书、延期，以及预约日期修改
- 管理员登录、图书管理、副本管理、按学号新增学生、新增管理员
- 管理员办理借书、还书、预约处理、罚金登记
- 管理员在图书详情中查看该书借阅历史，在学生详情中查看该生借阅历史
- 图书简介修改、本地附件上传、附件元数据登记
- 学生端支持立即借出；无可借馆藏时通过借出按钮自动加入预约队列
- 学生端预约需选择未来计划借出日期
- 图书、学生、管理员、借阅、还书和预约列表使用数据库分页
- 借阅、预约和违期记录使用数据库生成的日期业务长编码
- 首页展示历史借阅排行前十
- 表格点击表头升序/降序排序，默认第一列升序
- 数据库触发器、函数、存储过程、事务和业务序列表
- 系统运行日志写入 `logs/runtime.log`
- 业务操作审计日志写入 `logs/audit.log`
- Tabler 静态资源本地化，支持离线加载 UI 样式

## API 文档

后端 API 文档见：

```text
docs/api.md
```

核心 API 文件：

```text
backend/routes/auth.py
backend/routes/student.py
backend/routes/admin_dashboard.py
backend/routes/admin_books.py
backend/routes/admin_users.py
backend/routes/admin_circulation.py
```

## 测试

运行后端单元测试：

```bash
python -B -m unittest discover -s tests
```

当前测试覆盖：

- `tests/test_auth.py`：登录成功、登录失败、未登录访问、学生访问管理员接口权限校验
- `tests/test_book.py`：图书查询、分页、详情、简介修改、副本日期和附件上传
- `tests/test_borrow.py`：学生借出、还书、延期、借阅分页和无库存预约队列
- `tests/test_reservation.py`：预约提交、日期修改、取消和权限校验
- `tests/test_admin_flow.py`：管理员列表、学生详情、借书、还书、违期和罚金处理
- `tests/test_utils.py`：密码策略、学号格式、电话邮箱格式、SQL 转义工具
- `tests/helpers.py`：测试数据创建、登录和清理工具

前端构建验证：

```bash
cd frontend
npm run build
```

## 日志

系统运行日志位于：

```text
logs/runtime.log
```

系统运行日志记录应用创建、请求异常、数据库执行错误等运行状态。

业务操作审计日志位于：

```text
logs/audit.log
```

业务审计日志记录登录、预约、借阅、还书、修改密码等用户操作事件。

详细说明见：

```text
docs/日志说明.md
```
