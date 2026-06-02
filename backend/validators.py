import re


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_PATTERN = re.compile(r"^(1[3-9]\d{9}|0\d{2,3}-?\d{7,8})$")


def validate_email(email):
    return not email or bool(EMAIL_PATTERN.fullmatch(email.strip()))


def validate_phone(phone):
    return not phone or bool(PHONE_PATTERN.fullmatch(phone.strip()))
