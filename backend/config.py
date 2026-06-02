from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
LOG_DIR = BASE_DIR / "logs"

DB_NAME = os.environ.get("LIBRARY_DB_NAME", "db_lab2")
DB_USER = os.environ.get("LIBRARY_DB_USER", "root")
DB_PASSWORD = os.environ.get("LIBRARY_DB_PASSWORD", "123456")
MYSQL_BIN = os.environ.get("MYSQL_BIN", "mysql")

HOST = "127.0.0.1"
PORT = int(os.environ.get("LIBRARY_PORT", "8000"))
SESSION_COOKIE = "library_session"
SECRET_KEY = os.environ.get("LIBRARY_SECRET_KEY", "library-system-dev-secret")
