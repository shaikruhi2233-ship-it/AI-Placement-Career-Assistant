"""
Authentication service — password hashing (bcrypt) and JWT access tokens
(via python-jose).

Uses the `bcrypt` library directly rather than passlib's CryptContext:
passlib 1.7.4's backend self-test has a known incompatibility with
bcrypt>=4.1 (raises "password cannot be longer than 72 bytes" on its
internal self-check even for short passwords). Calling bcrypt directly
avoids that entirely.

SECURITY NOTE: SECRET_KEY below is a hardcoded demo value. In any real
deployment, set it from an environment variable
(`os.environ["JWT_SECRET_KEY"]`) and never commit it to source control.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-secret-change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days, convenient for a demo/student project


def hash_password(password: str) -> str:
    # bcrypt has a 72-byte input limit; truncate defensively.
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pw_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pw_bytes, hashed_password.encode("utf-8"))


def create_access_token(student_id: int, email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(student_id), "email": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[int]:
    """Returns the student_id encoded in the token, or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        student_id = payload.get("sub")
        return int(student_id) if student_id is not None else None
    except JWTError:
        return None
