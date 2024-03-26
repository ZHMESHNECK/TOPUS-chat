from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from TASKER.core.security import chat_id_generator, decode_token
from TASKER.core.config import get_session, templates
from TASKER.db.chat_db import get_history_chat, get_or_create_chat, save_message
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


class ConnectionManager:
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


private_manager = ConnectionManager()


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
