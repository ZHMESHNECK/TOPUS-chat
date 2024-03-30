from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from TASKER.core.security import chat_id_generator, decode_token
from TASKER.core.config import get_session, templates
from TASKER.db.chat_db import get_history_chat, get_or_create_chat, save_message
from TASKER.db.user_db import set_user_status
from typing import Dict, List


chat = APIRouter(prefix='/chat', tags=['chat'])


# @chat.get('/private_chat')
# async def login(request: Request):
#     return templates.TemplateResponse('private_chat.html', {'request': request})
@chat.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket")
    await websocket.close()


class PrivateManager:
    """ Менеджер для приватних повідомлень
    """

    def __init__(self):
        self.connections: Dict[str, List[WebSocket]] = {}

    def register_websocket(self, chat_id: str, websocket: WebSocket) -> None:

        if chat_id not in self.connections:
            self.connections[chat_id] = []
        self.connections[chat_id].append(websocket)

    async def broadcast(self, chat_id: str, message: str, sender_id: int, friend_id: int, add_to_db: bool, db: AsyncSession = None) -> None:
        if chat_id not in self.connections:
            return

        if add_to_db:
            await self.save_message_to_db(chat_id=chat_id, message=message, sender=sender_id, friend_id=friend_id, db=db)

        for websocket in self.connections[chat_id]:
            await websocket.send_text(message)

    def disconnect(self, chat_id, websocket: WebSocket):
        chat: list = self.connections.get(chat_id)
        chat.remove(websocket)

    @staticmethod
    async def save_message_to_db(chat_id: str, message: str, sender: int, friend_id, db: AsyncSession) -> None:
        await save_message(chat_id=chat_id, message=message, sender=sender, friend_id=friend_id, db=db)


class UserManager:
    """ Менеджер для спільного чату, + статус юзера ( online/offline )
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        self.active_connections.append(
            {'websocket': websocket, 'user_id': user_id})
        # Оновлення статусу користувача на "онлайн" в базі даних
        await self.update_user_status(user_id=user_id, online=True, db=db)

    async def disconnect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        # Видалення з'єднання з активних з'єднань
        for connection in self.active_connections:
            if connection['websocket'] == websocket and connection['user_id'] == user_id:
                self.active_connections.remove(connection)
                break
        # Оновлення статусу користувача на "офлайн" в базі даних
        await self.update_user_status(user_id=user_id, online=False, db=db)

    async def update_user_status(self, user_id: int, online: bool, db: AsyncSession):
        await set_user_status(user_id=user_id, online=online, db=db)

    async def broadcast_message(self, message: str):
        for connection in self.active_connections:
            await connection['websocket'].send_text(message)


private_manager = PrivateManager()
user_manager = UserManager()


@chat.get('/get_history_chat/{friend_id}')
async def get_last_messages(friend_id: int, token: str = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    chat_id = chat_id_generator(token['id'], friend_id)
    messages = await get_history_chat(chat_id=chat_id, db=db)
    return JSONResponse(status_code=status.HTTP_200_OK, content=messages)


@chat.get('/start_private_chat/{friend_id}')
async def start_private_chat(friend_id: int, token: str = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    if token['id'] == friend_id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Собі не можна написати')
    chat_id = chat_id_generator(token['id'], friend_id)
    await get_or_create_chat(chat_id=chat_id, user_id=token['id'], friend_id=friend_id, db=db)

    return JSONResponse(status_code=status.HTTP_200_OK, content='')


@chat.websocket('/private_chat/{friend_id}')
async def private_chat(friend_id: int, websocket: WebSocket, token: str = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    if token['id'] == friend_id:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content='Собі не можна написати')
    chat_id = chat_id_generator(token['id'], friend_id)

    private_manager.register_websocket(chat_id, websocket)
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            await private_manager.broadcast(chat_id=chat_id, message=data, sender_id=token['id'], friend_id=friend_id, db=db, add_to_db=True)

    except WebSocketDisconnect:
        private_manager.disconnect(chat_id, websocket)


@chat.websocket('/public_chat')
async def public_chat(websocket: WebSocket, user_id: int, db: AsyncSession = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    try:
        await user_manager.connect(websocket, user_id, db)
        await websocket.accept()

        while True:
            data = await websocket.receive_text()
            await user_manager.broadcast_message(data)

    except WebSocketDisconnect:
        await user_manager.disconnect(websocket, user_id, db=db)
