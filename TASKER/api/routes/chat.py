from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, WebSocketException
from TASKER.core.security import chat_id_generator, decode_token
from TASKER.core.config import get_session
from TASKER.api.schemas.users import UserFToken
from TASKER.db.chat_db import get_history_chat, get_or_create_chat, rm_all_noti, save_message
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

    def __init__(self, user_manage: 'UserManager'):
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
            if mes:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA, reason='Помилка при збереженні повідомлення')
        # Відправка всім підключенним юзерам
        for websocket in self.connections[chat]:
            await websocket.send_text(f'private:{sender_id}:{message}')

        # Якщо юзер онлайн но не підключен до чату
        if len(self.connections[chat]) < 2:
            friend_socket = self.user_manager.active_connections.get(
                friend_id, None)
            if friend_socket not in self.connections[chat]:
                await friend_socket.send_text(f'private:{sender_id}:{message}')

    def disconnect(self, chat, websocket: WebSocket):
        chat: list = self.connections.get(chat)
        if chat:
            chat.remove(websocket)

    @staticmethod
    async def save_message_to_db(chat: str, message: str, sender: int, friend_id, db: AsyncSession) -> None:
        return await save_message(chat=chat, message=message, sender=sender, friend_id=friend_id, db=db)


class UserManager:
    """ Менеджер для спільного чату, + статус юзера ( online/offline )
    """

    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}  # id

    async def connect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        self.active_connections[user_id] = websocket
        # Оновлення статусу користувача на "онлайн" в базі даних
        await self.update_user_status(user_id=user_id, online=True, db=db)

    async def disconnect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        # Видалення з'єднання з активних з'єднань
        self.active_connections.pop(user_id, None)
        # Оновлення статусу користувача на "офлайн" в базі даних
        await self.update_user_status(user_id=user_id, online=False, db=db)

    async def update_user_status(self, user_id: int, online: bool, db: AsyncSession):
        await set_user_status(user_id=user_id, online=online, db=db)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            await connection['websocket'].send_text(message)


user_manager = UserManager()
private_manager = PrivateManager(user_manager)


@chat.get('/get_history_chat/{friend_id}')
async def get_last_messages(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    chat_id = chat_id_generator(token.id, friend_id)
    messages = await get_history_chat(chat_value=chat_id, db=db)
    await rm_all_noti(user_id=token.id, friend_id=friend_id, db=db)
    return JSONResponse(status_code=status.HTTP_200_OK, content=messages)


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
            await private_manager.broadcast(chat=chat, message=data, sender_id=user_id, friend_id=friend_id, db=db, add_to_db=False)

    except WebSocketDisconnect:
        private_manager.disconnect(chat, websocket)


@chat.websocket('/public_chat')
async def public_chat(websocket: WebSocket, user_id: int, db: AsyncSession = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    try:
        await user_manager.connect(websocket, user_id, db)
        await websocket.accept()

        while True:
            data = await websocket.receive_text()
            await user_manager.broadcast_message(data)

    except WebSocketDisconnect:
        await user_manager.disconnect(websocket, user_id, db=db)
