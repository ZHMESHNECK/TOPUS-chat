from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from TASKER.core.security import hash_password, generate_token
from TASKER.api.schemas.users import Login, User
from TASKER.db.models import UserDB
import logging


async def user_registration(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Нікнейм зайнятий, оберіть інший")

    data.password = hash_password(data.password)
    new_user = UserDB(username=data.username, password=data.password)

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        logging.error('user_registration-Integrity', exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Помилка при реєстрації")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "Успішно зараєстровано", "token": generate_token(new_user)})


async def user_login(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Невірний пароль або логін")

    if user.password != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Невірний пароль або логін')
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Успіх", "token": generate_token(user)})
