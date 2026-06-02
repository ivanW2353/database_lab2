import base64
import hashlib
import hmac
import re
import secrets


PASSWORD_POLICY_MESSAGE = "密码至少 6 位，且只能包含数字或字母"
PASSWORD_POLICY = re.compile(r"^[A-Za-z0-9]{6,}$")


def validate_password(password):
    return bool(password and PASSWORD_POLICY.fullmatch(password))


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return "pbkdf2_sha256$120000$%s$%s" % (
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password, stored):
    try:
        algo, rounds, salt, digest = stored.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        new_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), base64.b64decode(salt), int(rounds))
        return hmac.compare_digest(base64.b64encode(new_digest).decode("ascii"), digest)
    except Exception:
        return False
