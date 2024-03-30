from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import and_, case
from fastapi.responses import JSONResponse
from TASKER.db.models import NotificationDB
from fastapi import HTTPException, status
from typing import Dict
import logging


async def get_count_notification(token: Dict, db: AsyncSession):
    statement = (
        select(
            func.sum(
                case(
                    (
                        (NotificationDB.friend_request_id != None, 1)
                    ),
                    else_=0
                )
            ).label('unread_friend_requests'),
            func.sum(
                case(
                    (
                        (NotificationDB.message_id != None, 1)
                    ),
                    else_=0
                )
            ).label('unread_messages')).where(and_(
                NotificationDB.username == token['username'],
                NotificationDB.is_read == False)).group_by(NotificationDB.username).correlate_except(NotificationDB))

    try:
        notifications = await db.execute(statement)
        notifications = notifications.first()
        return notifications
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def friend_req_noti(token: Dict, db: AsyncSession):
    statement = select(NotificationDB).filter(and_(
        NotificationDB.username == token['username'],
        NotificationDB.is_read == False,
        NotificationDB.friend_request_id != None))
    fields = ['id', 'username', 'online', 'last_seen']
    try:
        result_user = await db.execute(statement)
        result_user = result_user.scalars().all()
        if result_user:
            # список словарів з юзерами які надіслали запит на "дружбу"
            list_user = []
            for user in result_user:
                user_dict = user.friend_request.sender.as_dict(fields=fields)
                # Отримуємо список ідентифікаторів друзів користувача
                friend_ids = [friend.id for friend in result_user]
                # Перевіряємо, чи є користувач у друзях
                user_dict['is_friend'] = token['id'] in friend_ids
                user_dict['reque'] = True
                list_user.append(user_dict)

            return JSONResponse(status_code=status.HTTP_200_OK, content=list_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content='')
    except:
        logging.error(msg='friend_req_noti', exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
