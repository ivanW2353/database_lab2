import subprocess

from .config import BASE_DIR, DB_NAME, DB_PASSWORD, DB_USER, MYSQL_BIN
from .logging_config import RUNTIME_LOGGER


def q(value):
    if value is None:
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def like(value):
    return "%" + str(value).replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"


def mysql(sql, fetch=False, database=True):
    cmd = [
        MYSQL_BIN,
        f"-u{DB_USER}",
        f"-p{DB_PASSWORD}",
        "--default-character-set=utf8mb4",
        "--batch",
        "--raw",
    ]
    if database:
        cmd.append(f"--database={DB_NAME}")
    cmd.append(f"--execute={sql}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=BASE_DIR)
    if result.returncode != 0:
        msg = result.stderr.strip() or result.stdout.strip()
        RUNTIME_LOGGER.error("mysql_error sql=%s error=%s", " ".join(sql.split()), msg)
        raise RuntimeError(msg)
    if not fetch:
        return []
    lines = [line for line in (result.stdout or "").splitlines() if line.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        values = line.split("\t")
        rows.append({headers[i]: (values[i] if i < len(values) and values[i] != "NULL" else None) for i in range(len(headers))})
    return rows


def scalar(sql, default=None):
    rows = mysql(sql, fetch=True)
    if not rows:
        return default
    return next(iter(rows[0].values()))
