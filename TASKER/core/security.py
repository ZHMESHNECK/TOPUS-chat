from datetime import datetime, timedelta, timezone
from TASKER.core.config import secret_jwt, algorithm
from TASKER.db.models import UserDB
import hashlib
import jwt


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 algorithm."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_token(user: UserDB) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"exp": exp, "username": user.username, "role": user.role.value}
    return jwt.encode(payload, secret_jwt, algorithm=algorithm)


def decode_token(token: str):
    return jwt.decode(token, secret_jwt, algorithms=algorithm)
