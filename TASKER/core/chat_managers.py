from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, status, WebSocketException
from TASKER.core.utils import send_message_json
from TASKER.db.chat_db import create_group, get_or_create_chat, save_message
from TASKER.db.user_db import set_user_status
from typing import Dict, List


class PrivateManager:
    """ Менеджер для приватних повідомлень
    """

    def __init__(self, user_manage: 'PublicManager'):
        self.user_manager = public_manager
        self.connections: Dict[str, List[WebSocket]] = {}

    async def register_websocket(self, chat: str, user_id: int, friend_id: int, websocket: WebSocket, db: AsyncSession) -> None:

        if chat not in self.connections:
            self.connections[chat] = []
        self.connections[chat].append(websocket)
        chat = await get_or_create_chat(
            chat=chat, user_id=user_id, friend_id=friend_id, db=db)
        if not chat:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason='Помилка при підключенні')

    async def broadcast(self, chat: str, message: str, sender_id: int, friend_id: int, add_to_db: bool, db: AsyncSession = None) -> None:
        if chat not in self.connections:
            return

        if add_to_db:
            mes = await self.save_message_to_db(chat=chat, message=message, sender=sender_id, friend_id=friend_id, db=db)
            if not mes:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA, reason='Помилка при збереженні повідомлення')
        # # Відправка всім підключенним юзерам
        # for websocket in self.connections[chat]:
        #     await websocket.send_json(send_message_json(type='private', sender=sender_id, message=message))

        # Якщо юзер онлайн но не підключен до чату
        # if len(self.connections[chat]) < 2:
        friend_socket = self.user_manager.active_connections.get(
            friend_id, None)
        self_socket = self.user_manager.active_connections.get(
            sender_id, None)

        # Відправлення отримувачу
        if friend_socket:
            await friend_socket.send_json(send_message_json(type='private', sender=sender_id, message=message))

        # Відправлення собі
        if self_socket:
            await self_socket.send_json(send_message_json(type='private', sender=sender_id, message=message))

    def disconnect(self, chat, websocket: WebSocket):
        chat: list = self.connections.get(chat)
        if chat:
            chat.remove(websocket)

    @staticmethod
    async def save_message_to_db(chat: str, message: str, sender: int, friend_id, db: AsyncSession) -> None:
        return await save_message(chat=chat, message=message, sender=sender, friend_id=friend_id, db=db, type='private')


class PublicManager:
    """ Менеджер для спільного чату, + статус юзера ( online/offline )
    """

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  # id

    async def connect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = websocket
            # Оновлення статусу користувача на "онлайн" в базі даних
            await self.update_user_status(user_id=user_id, online=True, db=db)
            await self.broadcast_online_offline(user=user_id, online=True)

    async def disconnect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        # Видалення з'єднання з активних з'єднань
        self.active_connections.pop(user_id, None)
        # Оновлення статусу користувача на "офлайн" в базі даних
        await self.update_user_status(user_id=user_id, online=False, db=db)
        await self.broadcast_online_offline(user=user_id, online=False)

    async def update_user_status(self, user_id: int, online: bool, db: AsyncSession):
        await set_user_status(user_id=user_id, online=online, db=db)

    async def broadcast(self, message: str, sender_id: int, username: str, add_to_db: bool, db: AsyncSession = None) -> None:

        if add_to_db:
            mes = await self.save_message_to_db(message=message, sender_id=sender_id, username=username, db=db)
            if not mes:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA, reason='Помилка при збереженні повідомлення')

        # Відправка всім підключенним юзерам
        for websocket in self.active_connections.values():
            await websocket.send_json(send_message_json(type='public', sender=username, message=message))

    @staticmethod
    async def save_message_to_db(message: str, sender_id: int, username: int, db: AsyncSession) -> None:
        return await save_message(message=message, sender=sender_id, username=username, db=db, type='public')

    async def broadcast_online_offline(self, user: int, online: bool):
        for user_id, ws in self.active_connections.items():
            if user_id != user:
                await ws.send_json({'type': 'update_status', 'user_id': user, 'online': online})


class GroupManager:
    """ Менеджер для груп
    """

    def __init__(self, user_manage: 'PublicManager'):
        self.group_manager = public_manager
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, chat: str, user_id: int, websocket: WebSocket, db: AsyncSession) -> None:
        ...


# Online chats managers
public_manager = PublicManager()
private_manager = PrivateManager(public_manager)
group_manager = GroupManager(public_manager)
