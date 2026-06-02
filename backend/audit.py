from .logging_config import AUDIT_LOGGER


def log_event(action, user=None, **fields):
    identity = "anonymous"
    if user:
        identity = f"{user.get('role')}:{user.get('no')}:{user.get('login')}"
    detail = " ".join(f"{k}={v}" for k, v in fields.items())
    AUDIT_LOGGER.info("action=%s user=%s %s", action, identity, detail)
