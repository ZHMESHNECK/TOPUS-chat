from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, update
from fastapi.responses import JSONResponse
from fastapi import WebSocketException, status
from TASKER.api.schemas.chat import Chat
from TASKER.db.models import ChatDB, ChatUserDB, MessageDB, NotificationMessageDB
from typing import List
import logging


async def get_or_create_chat(chat: str, user_id: int, friend_id: int, db: AsyncSession):
    statement = select(ChatDB).filter(ChatDB.chat == chat)
    try:
        alrady_exists = await db.execute(statement)
        alrady_exists = alrady_exists.scalar_one_or_none()

        if alrady_exists:
            return alrady_exists
        else:
            new_chat = ChatDB(chat=chat)
            db.add(new_chat)
            await db.commit()
            await db.refresh(new_chat)

            check = await add_user_to_chat(chat_id=new_chat.id, user_id=[user_id, friend_id], db=db)
            if not check:
                return False

            return new_chat
    except Exception:
        logging.error(msg='get_or_create_chat', exc_info=True)
        await db.rollback()
        return False


async def add_user_to_chat(chat_id: int, user_id: List, db: AsyncSession):
    user1 = ChatUserDB(chat_id=chat_id,  user_id=user_id[0])
    user2 = ChatUserDB(chat_id=chat_id, user_id=user_id[1])
    try:
        db.add_all([user1, user2])
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        logging.error(msg='add_user_to_chat', exc_info=True)
        return False


async def save_message(chat: str, sender: int, message: str, friend_id: int, db: AsyncSession):
    try:
        chat: Chat = await get_or_create_chat(chat=chat, user_id=sender, friend_id=friend_id, db=db)
        if chat:
            db_message = MessageDB(
                chat_id=chat.id,
                sender_id=sender,
                message=message
            )
            db.add(db_message)
            await db.commit()
            await db.refresh(db_message)
            await save_notification(chat=chat, user_id=friend_id, sender_id=sender, message=db_message.id, db=db)
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception:
        await db.rollback()
        logging.error(msg='save message', exc_info=True)
        return WebSocketException(
            code=status.WS_1003_UNSUPPORTED_DATA)


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


async def get_history_chat(chat_value: str, db: AsyncSession):
    statement = select(ChatDB).where(ChatDB.chat == chat_value)

    chat = await db.execute(statement)
    chat = chat.scalar_one_or_none()

    if chat:
        statement2 = select(MessageDB).filter(
            MessageDB.chat_id == chat.id).limit(100)
        try:
            history = await db.execute(statement2)
            history = history.scalars().all()
            return [msg.as_dict() for msg in history]
        except:
            await db.rollback()
            logging.error(msg='get_history_chat', exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='')
    return None


async def rm_all_noti(user_id: int, friend_id: int,  db: AsyncSession):
    statement = update(NotificationMessageDB).where(and_(
        NotificationMessageDB.user_id == user_id,
        NotificationMessageDB.sender_id == friend_id,
        NotificationMessageDB.is_read == False
    )).values(is_read=True)

    try:
        await db.execute(statement)
        await db.commit()
    except:
        logging.error(msg='rm_all_noti', exc_info=True)
