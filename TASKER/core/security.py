from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from TASKER.core.config import get_session, secret_jwt, algorithm
from TASKER.db.models import UserDB
import hashlib
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 algorithm."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def generate_token(user: UserDB) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {
        "exp": exp,
        "id": user.id,
        "username": user.username,
        "role": user.role
    }
    return jwt.encode(payload, secret_jwt, algorithm=algorithm)


def decode_token(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)):
    try:
        payload = jwt.decode(token, secret_jwt, algorithms=algorithm)
        if not payload:
            raise HTTPException(status_code=401, detail="Невірні данні")
        return payload
    except jwt.ExpiredSignatureError:
        return HTTPException(status_code=401, detail='Потрібно авторизуватись')
    except jwt.InvalidTokenError:
        return HTTPException(status_code=401, detail='Невірні данні')
