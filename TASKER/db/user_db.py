from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
from TASKER.core.security import hash_password, generate_token
from TASKER.api.schemas.users import Login, StatusFriend
from TASKER.api.schemas.utils import SearchRequest
from TASKER.db.models import UserDB, FriendshipDB, FriendRequestDB
import logging


async def user_registration(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Нікнейм зайнятий, оберіть інший')

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
                            detail='Помилка при реєстрації')

    token = generate_token(new_user)
    response = JSONResponse(status_code=status.HTTP_201_CREATED, content='')
    response.set_cookie(key='TOPUS', value=token, httponly=True)
    return response


async def user_login(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Невірний пароль або логін')
    if user.password != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Невірний пароль або логін')

    token = generate_token(user)
    response = JSONResponse(status_code=status.HTTP_200_OK, content='')
    response.set_cookie(key='TOPUS', value=token, httponly=True)
    return response


async def user_send_request_friend(username: str, friend_name: str,  db: AsyncSession):
    if username == friend_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Не можна відправити собі запит')

    statement_check_friendship = select(FriendRequestDB).filter(and_(
        FriendRequestDB.sender_name == username,
        FriendRequestDB.receiver_name == friend_name))

    check_friendship = await db.execute(statement_check_friendship)
    check_friendship = check_friendship.scalar_one_or_none()
    if check_friendship:
        if check_friendship.status in (StatusFriend.pending.value, StatusFriend.accepted.value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=(
                                'Запит вже надіслано', 'Вже у друзях')[check_friendship.status == StatusFriend.accepted.value])

    statement = select(UserDB).filter(
        and_(UserDB.username.in_([username, friend_name])))
    users = await db.execute(statement)
    users = users.scalars().all()

    if len(users) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Профіль не знайдено')
    user, friend = users

    if user.username == friend_name:
        friend, user = user, friend
    try:
        request = FriendRequestDB(
            sender_name=user.username, receiver_name=friend.username)
        db.add(request)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Надіслано')
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Помилка додавання запиту на дружбу до бази даних')


async def accept_friend_request(username: str, friend_name: str, db: AsyncSession):
    if username == friend_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Не можна прийняти свій запит')

    statement = select(FriendRequestDB).filter(
        and_(FriendRequestDB.sender_name == friend_name,
             FriendRequestDB.receiver_name == username,
             FriendRequestDB.status == StatusFriend.pending.value))

    try:
        friend_request = await db.execute(statement)
        friend_request = friend_request.scalar_one_or_none()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Помилка сервера')

    if not friend_request:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Запит не знайдено')

    friend_request.status = 'accepted'
    friendship = FriendshipDB(
        user_name=friend_request.sender_name, friend_name=friend_request.receiver_name)

    db.add(friendship)
    try:
        await db.commit()
        return JSONResponse(status_code=status.HTTP_201_CREATED, content='Додано до друзів')
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Помилка сервера')


async def declain_friend_request(username: str, friend_name: str, db: AsyncSession):
    if username == friend_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail='Ви не надсилали собі запит :)')

    statement = select(FriendRequestDB).where(or_(and_(
        FriendRequestDB.sender_name == username,
        FriendRequestDB.receiver_name == friend_name),
        and_(
        FriendRequestDB.sender_name == friend_name,
        FriendRequestDB.receiver_name == username)
    ))

    try:
        friend_request = await db.execute(statement)
        friend_request = friend_request.scalar_one_or_none()
        if not friend_request:
            raise HTTPException(status.HTTP_404_NOT_FOUND,
                                detail='Запит не занйдено')
        await db.delete(friend_request)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Запит відхилено')

    except:
        await db.rollback()
        logging.error(msg='declain_friend_request', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Помилка сервера')


async def delete_friendship(username: str, friend_name: str, db: AsyncSession):
    statement = select(FriendshipDB).filter(or_(and_(
        FriendshipDB.user_name == username,
        FriendshipDB.friend_name == friend_name),
        and_(
        FriendshipDB.user_name == friend_name,
        FriendshipDB.friend_name == username
    )))

    friendship = await db.execute(statement)
    friendship = friendship.scalar_one_or_none()
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Зв'язок не знайдено")

    statement2 = select(FriendRequestDB).filter(or_(and_(
        FriendRequestDB.sender_name == username,
        FriendRequestDB.receiver_name == friend_name),
        and_(
        FriendRequestDB.sender_name == friend_name,
        FriendRequestDB.receiver_name == username

    )))
    friend_request = await db.execute(statement2)
    friend_request = friend_request.scalar_one_or_none()

    try:
        await db.delete(friend_request)
        await db.delete(friendship)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Видалено з друзів')
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Помилка сервера')


async def get_list_friends(token: str, db: AsyncSession):
    statement = select(FriendshipDB).filter(or_(and_(
        FriendshipDB.user_name == token['username']),
        and_(
        FriendshipDB.friend_name == token['username'],
    )))
    friends = await db.execute(statement)
    friends = friends.scalars().all()

    return [friend.as_dict() for friend in friends]


async def get_search(data: SearchRequest, token: dict, db: AsyncSession):
    statement_user = select(UserDB).filter(or_(
        UserDB.username.ilike(f'%{data.request}%'),
        UserDB.username.ilike(f'{data.request}%'),
        UserDB.username.ilike(f'%{data.request}')),
        and_(UserDB.id != token['id'])).limit(15)

    result_user = await db.execute(statement_user)
    result_user = result_user.scalars().all()
    # Поля які потрібно повернути
    fields = ['id', 'username', 'online', 'last_seen']

    if result_user:
        list_user = []
        # list_friends = await get_list_friends(token=token, db=db)
        for user in result_user:
            user_dict = user.as_dict(fields=fields)
            # Отримуємо список ідентифікаторів друзів користувача
            friend_ids = [friend.id for friend in user.friends]
            # Перевіряємо, чи є користувач у друзях
            user_dict['is_friend'] = token['id'] in friend_ids
            list_user.append(user_dict)

        return list_user
    response = JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='')
    return response
