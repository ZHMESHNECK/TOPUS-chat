from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import WebSocket, status, WebSocketException
from TASKER.core.utils import send_message_json
from TASKER.db.chat_db import get_group_chat, get_or_create_chat, save_message
from TASKER.db.models import ChatDB
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

    def disconnect(self, chat, websocket: WebSocket):
        chat: list = self.connections.get(chat)
        if chat and websocket in chat:
            chat.remove(websocket)

    async def broadcast(self, chat: str, message: str, sender_id: int, friend_id: int, websocket: WebSocket, add_to_db: bool, db: AsyncSession = None) -> None:
        if chat not in self.connections:
            return

        if add_to_db:
            mes = await self.save_message_to_db(chat=chat, message=message, sender=sender_id, friend_id=friend_id, db=db)
            if not mes:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA, reason='Помилка при збереженні повідомлення')

        friend_socket = self.user_manager.active_connections.get(
            friend_id, None)

        # Відправлення отримувачу
        if friend_socket:
            await friend_socket.send_json(send_message_json(type='private', sender=sender_id, message=message))

        # Відправлення собі
        await websocket.send_json(send_message_json(type='private', sender=sender_id, message=message))

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

    async def disconnect(self, user_id: int, db: AsyncSession):
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
        self.connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, group_title: str, websocket: WebSocket, db: AsyncSession) -> None:
        chat: ChatDB = await get_group_chat(group_title=group_title, db=db)
        if not chat:
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR, reason='Помилка при підключенні')

        if group_title not in self.connections:
            self.connections[chat.title] = []
        self.connections[chat.title].append(websocket)

    def disconnect(self, group_title, websocket: WebSocket):
        chat: list = self.connections.get(group_title)
        if chat and websocket in chat:
            chat.remove(websocket)

    async def broadcast(self, message: str, sender_id: int, username: str, group_title: str, add_to_db: bool, db: AsyncSession):
        if add_to_db:
            mes = await self.save_message_to_db(message=message, sender_id=sender_id, group_title=group_title, username=username, db=db)
            if not mes:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA, reason='Помилка при збереженні повідомлення')

        # Відправка юзерам які онлайн та є в группі
        for websocket in self.connections[group_title]:
            await websocket.send_json(send_message_json(type='group', sender=username, message=message))

    @staticmethod
    async def save_message_to_db(message: str, sender_id: int, username: int, group_title: str, db: AsyncSession):
        return await save_message(message=message, sender=sender_id, username=username, chat=group_title, db=db, type='group')


# Online chats managers
public_manager = PublicManager()
private_manager = PrivateManager(public_manager)
group_manager = GroupManager(public_manager)
