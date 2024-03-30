from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import status
from TASKER.core.security import hash_password, generate_token
from TASKER.api.schemas.users import Login, StatusFriend
from TASKER.api.schemas.utils import SearchRequest
from TASKER.core.utils import get_list_user
from TASKER.db.models import UserDB, FriendshipDB, FriendRequestDB, NotificationDB
from typing import Dict
import logging


async def user_registration(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Нікнейм зайнятий, оберіть інший')

    data.password = hash_password(data.password)
    new_user = UserDB(username=data.username, password=data.password)

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except IntegrityError:
        logging.error('user_registration-Integrity', exc_info=True)
        await db.rollback()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content='Помилка при реєстрації')

    token = generate_token(new_user)
    response = JSONResponse(status_code=status.HTTP_201_CREATED, content='')
    response.set_cookie(key='TOPUS', value=token, httponly=True)
    return response


async def user_login(data: Login, db: AsyncSession):
    statement = select(UserDB).where(UserDB.username == data.username)
    user = await db.execute(statement)
    user = user.scalar_one_or_none()
    if not user:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Невірний пароль або логін')
    if user.password != hash_password(data.password):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Невірний пароль або логін')

    token = generate_token(user)
    response = JSONResponse(status_code=status.HTTP_200_OK, content='')
    response.set_cookie(key='TOPUS', value=token, httponly=True)
    return response


async def user_send_request_friend(username: str, friend_name: str,  db: AsyncSession):
    if username == friend_name:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Не можна відправити собі запит')

    statement_check_friendship = select(FriendRequestDB).filter(and_(
        FriendRequestDB.sender_name == username,
        FriendRequestDB.receiver_name == friend_name))

    check_friendship = await db.execute(statement_check_friendship)
    check_friendship = check_friendship.scalar_one_or_none()
    if check_friendship:
        if check_friendship.status in (StatusFriend.pending.value, StatusFriend.accepted.value):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=(
                'Запит вже надіслано', 'Вже у друзях')[check_friendship.status == StatusFriend.accepted.value])

    statement = select(UserDB).filter(
        and_(UserDB.username.in_([username, friend_name])))
    users = await db.execute(statement)
    users = users.scalars().all()

    if len(users) != 2:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Профіль не знайдено')
    user, friend = users

    if user.username == friend_name:
        friend, user = user, friend
    try:
        # Створюємо запит
        request = FriendRequestDB(
            sender_name=user.username, receiver_name=friend.username)
        db.add(request)
        await db.commit()
        await db.refresh(request)

        # Створюємо повідомлення
        notification = NotificationDB(
            username=friend_name, friend_request_id=request.id)
        db.add(notification)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Надіслано')
    except IntegrityError:
        await db.rollback()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content='Помилка додавання запиту на дружбу')


async def accept_friend_request(username: str, friend_name: str, db: AsyncSession):
    if username == friend_name:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Не можна прийняти свій запит')

    statement = select(FriendRequestDB).filter(
        and_(FriendRequestDB.sender_name == friend_name,
             FriendRequestDB.receiver_name == username,
             FriendRequestDB.status == StatusFriend.pending.value))

    try:
        friend_request = await db.execute(statement)
        friend_request = friend_request.scalar_one_or_none()
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка сервера')

    if not friend_request:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Запит не знайдено')

    friend_request.status = 'accepted'
    friendship = FriendshipDB(
        user_name=friend_request.sender_name, friend_name=friend_request.receiver_name)

    db.add(friendship)
    try:
        # Створюємо "Дружбу"
        await db.commit()
        await db.refresh(friend_request)
        # Помічаемо повідомлення як прочитане
        statement = select(NotificationDB).where(and_(
            NotificationDB.username == username,
            NotificationDB.friend_request_id == friend_request.id))
        notification = await db.execute(statement)
        notification = notification.scalar_one_or_none()
        if notification:
            notification.is_read = True

        db.add(notification)
        await db.commit()

        return JSONResponse(status_code=status.HTTP_201_CREATED, content='Додано до друзів')
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка сервера')


async def declain_friend_request(username: str, friend_name: str, db: AsyncSession):
    if username == friend_name:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content='Ви не надсилали собі запит :)')

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
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='Запит не знайдено')

        # Помічаемо повідомлення як прочитане
        statement = select(NotificationDB).where(and_(
            NotificationDB.username == username,
            NotificationDB.friend_request_id == friend_request.id))
        notification = await db.execute(statement)
        notification = notification.scalar_one_or_none()
        if not notification:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка сервера')
        notification.is_read = True

        db.add(notification)
        await db.delete(friend_request)
        await db.commit()

        return JSONResponse(status_code=status.HTTP_200_OK, content='Запит відхилено')

    except:
        await db.rollback()
        logging.error(msg='declain_friend_request', exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка сервера')


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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Зв'язок не знайдено")

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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка сервера')


async def get_list_friends(token: Dict, db: AsyncSession):
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
        and_(UserDB.id != token['id'])).order_by('username').limit(15)

    result_user = await db.execute(statement_user)
    result_user = result_user.scalars().all()

    if result_user:
        list_user = get_list_user(result_user, token)

        response = JSONResponse(
            status_code=status.HTTP_200_OK, content=list_user)
        return response
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='')


async def logout(request):
    response = JSONResponse(status_code=status.HTTP_200_OK, content='')
    response.delete_cookie(key='TOPUS')
    return response


async def set_user_status(user_id: int, online: bool, db: AsyncSession):
    try:
        user = await db.get(UserDB, user_id)
        if user:
            if not online:
                user.last_seen = datetime.now()
            user.online = online
            await db.commit()
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, content='Юзера не знайдено')
    except:
        logging.error(msg='set_user_status', exc_info=True)
