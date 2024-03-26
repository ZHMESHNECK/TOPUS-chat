from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, WebSocketException, status
from TASKER.db.models import Chat, ChatUser, MessageDB
from typing import List
import logging


async def get_or_create_chat(chat_id: str, user_id: int, friend_id: int, db: AsyncSession):
    statement = select(Chat).filter(Chat.chat == chat_id)
    try:
        alrady_exists = await db.execute(statement)
        alrady_exists = alrady_exists.scalar_one_or_none()

        if alrady_exists:
            return alrady_exists
        else:
            new_chat = Chat(chat=chat_id)
            db.add(new_chat)
            await db.commit()
            await db.refresh(new_chat)

            await add_user_to_chat(chat_id=new_chat.id, user_id=[user_id, friend_id], db=db)

            return new_chat
    except Exception as e:
        logging.error(msg='get_or_create_chat', exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def add_user_to_chat(chat_id: str, user_id: List, db: AsyncSession):
    user1 = ChatUser(chat_id=chat_id,  user_id=user_id[0])
    user2 = ChatUser(chat_id=chat_id, user_id=user_id[1])
    try:
        db.add_all([user1, user2])
        await db.commit()
    except Exception as e:
        logging.error(msg='add_user_to_chat', exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def save_message(chat_id, sender, message, friend_id, db: AsyncSession):
    try:
        chat = await get_or_create_chat(chat_id=chat_id, user_id=sender, friend_id=friend_id, db=db)
        if chat:
            db_message = MessageDB(
                chat_id=chat.id,
                sender_id=sender,
                message=message
            )
            db.add(db_message)
            await db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logging.error(msg='save message', exc_info=True)
        raise WebSocketException(code=status.WS_1003_UNSUPPORTED_DATA)


async def get_history_chat(chat_id: str, db: AsyncSession):
    statement = select(Chat).where(Chat.chat == chat_id)

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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return None
