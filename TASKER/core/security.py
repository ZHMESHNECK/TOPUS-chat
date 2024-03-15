import hashlib


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 algorithm."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
