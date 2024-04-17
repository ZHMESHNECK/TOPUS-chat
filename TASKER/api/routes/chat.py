from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, WebSocketException
from TASKER.core.security import chat_id_generator, decode_token
from TASKER.core.config import get_session
from TASKER.api.schemas.users import UserFToken
from TASKER.db.chat_db import get_history_chat, get_or_create_chat, get_public_history, rm_all_noti, save_message
from TASKER.db.user_db import set_user_status
from typing import Dict, List


chat = APIRouter(prefix='/chat', tags=['chat'])


@chat.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket")
    await websocket.close()


class PrivateManager:
    """ Менеджер для приватних повідомлень
    """

    def __init__(self, user_manage: 'PublicManager'):
        self.user_manager = user_manager
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
        # Відправка всім підключенним юзерам
        for websocket in self.connections[chat]:
            await websocket.send_text(f'private:{sender_id}:{message}')

        # Якщо юзер онлайн но не підключен до чату
        if len(self.connections[chat]) < 2:
            friend_socket = self.user_manager.active_connections.get(
                friend_id, None)
            if friend_socket and friend_socket not in self.connections[chat]:
                await friend_socket.send_text(f'private:{sender_id}:{message}')

    def disconnect(self, chat, websocket: WebSocket):
        chat: list = self.connections.get(chat)
        if chat:
            chat.remove(websocket)

    @staticmethod
    async def save_message_to_db(chat: str, message: str, sender: int, friend_id, db: AsyncSession) -> None:
        return await save_message(chat=chat, message=message, sender=sender, friend_id=friend_id, db=db)


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
            await websocket.send_text(f'public:{username}:{message}')

    @staticmethod
    async def save_message_to_db(message: str, sender_id: int, username: int, db: AsyncSession) -> None:
        return await save_message(message=message, sender=sender_id, username=username, db=db, is_private=False)

    async def broadcast_online_offline(self, user: int, online: bool):
        for user_id, ws in self.active_connections.items():
            if user_id != user:
                await ws.send_json({'type': 'update_status', 'user_id': user, 'online': online})


user_manager = PublicManager()
private_manager = PrivateManager(user_manager)


@chat.get('/get_history_chat/{friend_id}')
async def get_last_messages(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    chat_id = chat_id_generator(token.id, friend_id)
    messages = await get_history_chat(chat_value=chat_id, db=db)
    await rm_all_noti(user_id=token.id, friend_id=friend_id, db=db)
    if messages:
        return JSONResponse(status_code=status.HTTP_200_OK, content=messages)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка при завантаженні історії чату')


@chat.get('/get_history_public')
async def get_last_messages_public(token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    messages = await get_public_history(db=db)
    if messages:
        return JSONResponse(status_code=status.HTTP_200_OK, content=messages)
    elif messages == False:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Помилка при завантаженні історії чату')
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content='Історія порожня')


@chat.websocket('/private_chat/{user_id}/{friend_id}')
async def private_chat(user_id: int, friend_id: int, websocket: WebSocket, db: AsyncSession = Depends(get_session)):
    if user_id == friend_id:
        raise WebSocketException(
            code=status.WS_1007_INVALID_FRAME_PAYLOAD_DATA, reason='Собі не можна написати')
    chat = chat_id_generator(user_id, friend_id)

    await private_manager.register_websocket(chat=chat, user_id=user_id, friend_id=friend_id, websocket=websocket, db=db)
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await private_manager.broadcast(chat=chat, message=data, sender_id=user_id, friend_id=friend_id, db=db, add_to_db=True)

    except WebSocketDisconnect:
        private_manager.disconnect(chat, websocket)


@chat.websocket('/public_chat/{user_id}/{username}')
async def public_chat(websocket: WebSocket, user_id: int, username: str, db: AsyncSession = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        await user_manager.connect(websocket, user_id, db)
        await websocket.accept()

        while True:
            data = await websocket.receive_text()
            await user_manager.broadcast(message=data, username=username, sender_id=user_id, db=db, add_to_db=True)

    except WebSocketDisconnect:
        await user_manager.disconnect(websocket, user_id, db=db)
