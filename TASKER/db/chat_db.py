from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, delete, update
from fastapi import WebSocketException, status
from TASKER.api.schemas.chat import Chat
from TASKER.api.schemas.users import Role
from TASKER.api.schemas.utils import KickUser, UsersFromGroup, CreateGroupTitle
from TASKER.db.models import AdminsOfGroup, ChatDB, ChatUserDB, MessageDB, NotificationMessageDB
from typing import List, Optional
import logging


async def get_public_chat_id(db: AsyncSession):
    statement = select(ChatDB).where(ChatDB.chat == 'public')
    chat_id = await db.execute(statement)
    chat_id = chat_id.scalar_one_or_none()
    if chat_id:
        return chat_id
    else:
        chat = ChatDB(chat='public')
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat


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
    user1 = ChatUserDB(chat_id=chat_id, user_id=user_id[0])
    user2 = ChatUserDB(chat_id=chat_id, user_id=user_id[1])
    try:
        db.add_all([user1, user2])
        await db.commit()
        return True
    except Exception:
        await db.rollback()
        logging.error(msg='add_user_to_chat', exc_info=True)
        return False


async def save_message(sender: int, message: str, db: AsyncSession, type: str, username: Optional[str] = None, friend_id: Optional[int] = None, chat: Optional[str] = None):
    try:
        
        if type == 'private':
            chat: Chat = await get_or_create_chat(chat=chat, user_id=sender, friend_id=friend_id, db=db)
            db_message = MessageDB(
                chat_id=chat.id,
                sender_id=sender,
                message=message
            )
            db.add(db_message)

            await db.commit()
            await db.refresh(db_message)
            await save_notification(chat=chat, user_id=friend_id, sender_id=sender, message=db_message.id, db=db)

        elif type == 'public':
            chat: Chat = await get_public_chat_id(db)
            db_message = MessageDB(
                chat_id=chat.id,
                sender_id=sender,
                sender_username=username,
                message=message
            )
            db.add(db_message)
            await db.commit()

        else:
            return False

        return True
    except Exception:
        await db.rollback()
        logging.error(msg='save message', exc_info=True)
        return False


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
            return False
    return False


async def get_public_history(db: AsyncSession):
    statement = select(ChatDB).where(ChatDB.chat == 'public')
    try:
        pub_chat = await db.execute(statement)
        pub_chat = pub_chat.scalar_one_or_none()

        if not pub_chat:
            chat = ChatDB(chat='public')
            db.add(chat)
            await db.commit()
            await db.refresh(chat)

        statement2 = select(MessageDB).filter(
            MessageDB.chat_id == pub_chat.id).limit(100)
        pub_history = await db.execute(statement2)
        pub_history = pub_history.scalars().all()
        return [msg.as_dict() for msg in pub_history]

    except:
        await db.rollback()
        logging.error(msg='get_public_history', exc_info=True)
        return False


async def rm_all_noti(user_id: int, friend_id: int, db: AsyncSession):
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


async def create_group(data: CreateGroupTitle, user_id: int, db: AsyncSession):
    statement = select(ChatDB).where(ChatDB.chat == data.title).exists()

    try:
        result = await db.scalar(select(statement))
        if not result:
            group = ChatDB(chat=data.title)
            db.add(group)
            await db.commit()
            await db.refresh(group)
            user = ChatUserDB(chat_id=group.id, user_id=user_id)
            status_ = AdminsOfGroup(user_id=user_id, chat_id=group.id, status=Role.admin.value)
            db.add_all([user, status_])
            await db.commit()
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={'msg': 'Чат створенно', 'id': group.id})
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content='Чат вже існує, оберіть іншу назву')

    except:
        await db.rollback()
        logging.error(msg='create_group', exc_info=True)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='При створенні чату сталася помилка')


async def add_user_to_group(data: UsersFromGroup, owner: int, db: AsyncSession):
    list_of_users = data.users
    list_of_users.append(owner)
    statement = select(AdminsOfGroup).filter(
        AdminsOfGroup.chat_id == data.chat,
        AdminsOfGroup.user_id.in_(list_of_users)
    )

    try:
        result = await db.execute(statement)
        result = {user.user_id: user.status for user in result.scalars()}
        if result[owner] != Role.admin.value:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Ви не адмін чату')

        for user in data.users:
            # Check if the user is already in the group
            if user not in result and user != owner:
                new_user = AdminsOfGroup(user_id=user, chat_id=data.chat, status=Role.user.value)
                new_user_chat = ChatUserDB(user_id=user, chat_id=data.chat)
                db.add_all([new_user, new_user_chat])

        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content=f'Юзер{"и" if len(list_of_users)>2 else ""} успішно додан{"і" if len(list_of_users)>2 else ""} в чат')

    except:
        await db.rollback()
        logging.error(msg='add_user_to_group', exc_info=True)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='При доданні юзерів сталася помилка')


async def kick_from_group(data: KickUser, owner: int, db: AsyncSession):
    if data.user == owner:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Адмін не може себе видалити')

    admin_statement = select(AdminsOfGroup).where(and_(
        AdminsOfGroup.user_id == owner,
        AdminsOfGroup.chat_id == data.chat,
        AdminsOfGroup.status == Role.admin.value,
    )).exists()

    try:
        result = await db.scalar(select(admin_statement))
        if not result:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Не достатньо прав')
    except:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='При видаленні юзера сталася помилка')

    statement = delete(ChatUserDB).where(and_(
        ChatUserDB.user_id == data.user,
        ChatUserDB.chat_id == data.chat
    ))
    try:
        await db.execute(statement)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Успішно видалено')
    except:
        await db.rollback()
        logging.error(msg='kick_from_group', exc_info=True)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='При видаленні юзера сталася помилка')


async def delete_group(chat: str, chat_id: int, owner: int, db: AsyncSession):
    admin_statement = select(AdminsOfGroup).where(and_(
        AdminsOfGroup.user_id == owner,
        AdminsOfGroup.chat_id == chat_id,
        AdminsOfGroup.status == Role.admin.value,
    )).exists()

    try:
        result = await db.scalar(select(admin_statement))
        if not result:
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Не достатньо прав')

        statement = delete(ChatDB).where(ChatDB.chat == chat)
        await db.execute(statement)
        await db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK, content='Група видалена')
    except:
        await db.rollback()
        logging.error(msg='delete_group', exc_info=True)
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Не вдалося видалити групу')
