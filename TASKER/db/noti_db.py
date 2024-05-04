from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import and_, desc
from fastapi.responses import JSONResponse
from fastapi import HTTPException, WebSocketException, status
from TASKER.api.schemas.chat import Chat
from TASKER.core.utils import get_list_friend_req, get_list_message_req
from TASKER.api.schemas.users import StatusFriend, UserFToken
from TASKER.db.models import FriendRequestDB, NotificationFriendReqDB, NotificationMessageDB
import logging


async def get_count_notification(token: UserFToken, db: AsyncSession):
    statement = select(
        NotificationMessageDB.sender_id,
        func.count().label('unread_mess'),
    ).select_from(
        NotificationMessageDB
    ).where(
        NotificationMessageDB.user_id == token.id,
        NotificationMessageDB.is_read == False
    ).group_by(NotificationMessageDB.sender_id)

    try:
        notifications = await db.execute(statement)
        # notifications = notifications.scalars()
        # [(1:2), ...] - де 1 це id відправкника, 2 - кількість не прочитанних
        notifications = [(row.sender_id, row.unread_mess)
                         for row in notifications]
        total_unread_noti = sum(
            rows[1] for rows in notifications)

        requests_statement = select(
            func.count(NotificationFriendReqDB.id)
        ).where(
            NotificationFriendReqDB.user_id == token.id,
            NotificationFriendReqDB.is_read == False
        )
        noti_frie = await db.execute(requests_statement)
        noti_frie = noti_frie.fetchone()[0]
        return {'unread_mess': total_unread_noti, 'user_mes': dict(notifications), 'user_req': noti_frie}

    except:
        logging.error(msg='get_count_notification', exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def friend_req_noti(token: UserFToken, db: AsyncSession):
    """ Отримання юзерів які надіслали запит на дружбу

    Returns:
        JsonResponse:
    """
    statement = select(FriendRequestDB).filter(and_(
        FriendRequestDB.receiver_id == token.id,
        FriendRequestDB.status == StatusFriend.pending.value)).order_by(desc(FriendRequestDB.id))
    try:
        result_user = await db.execute(statement)
        result_user = result_user.scalars().all()
        if result_user:
            list_user = get_list_friend_req(result_user)
            return JSONResponse(status_code=status.HTTP_200_OK, content=list_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content='')
    except:
        logging.error(msg='friend_req_noti', exc_info=True)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def mess_req_noti(token: UserFToken, db: AsyncSession):
    """ Отримання юзерів які надіслали повідомлення

    Returns:
        JsonResponse:
    """
    statement = select(NotificationMessageDB).filter(
        and_(
            NotificationMessageDB.user_id == token.id,
            NotificationMessageDB.is_read == False)
    ).distinct(NotificationMessageDB.sender_id)

    try:
        result_user = await db.execute(statement)
        result_user = result_user.scalars().all()
        if result_user:
            list_user = get_list_message_req(result_user, token)

            return JSONResponse(status_code=status.HTTP_200_OK, content=list_user)
        return JSONResponse(status_code=status.HTTP_200_OK, content='')
    except:
        logging.error(msg='friend_req_noti', exc_info=True)
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def save_notification(chat: Chat, user_id: int, sender_id: int, message: int, db: AsyncSession):
    try:
        db_message = NotificationMessageDB(
            user_id=user_id,
            sender_id=sender_id,
            chat_id=chat.id,
            message_id=message
        )
        db.add(db_message)
        await db.commit()
    except Exception:
        await db.rollback()
        logging.error(msg='save notification message', exc_info=True)
        return WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA)
