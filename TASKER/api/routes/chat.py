from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, WebSocketException
from TASKER.core.chat_managers import private_manager, public_manager, group_manager
from TASKER.core.security import chat_id_generator, decode_token
from TASKER.core.config import get_session
from TASKER.api.schemas.utils import KickUser, UsersFromGroup, CreateGroupTitle
from TASKER.api.schemas.users import UserFToken
from TASKER.db.chat_db import add_user_to_group, create_group, delete_group, get_history_chat, get_public_history, group_history, kick_from_group, rm_all_noti


chat = APIRouter(prefix='/chat', tags=['chat'])


@chat.websocket("/ws")
async def websocket(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Hello WebSocket")
    await websocket.close()


@chat.get('/get_history_chat/{friend_id}')
async def get_last_messages(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    await rm_all_noti(user_id=token.id, friend_id=friend_id, db=db)
    chat_id = chat_id_generator(token.id, friend_id)
    return await get_history_chat(chat_value=chat_id, db=db)


@chat.get('/get_history_public')
async def get_last_messages_public(token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await get_public_history(db=db)


@chat.get('/get_group_history/{group_title}')
async def get_group_history(group_title: str, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    h_group = await group_history(group_title=group_title, db=db)
    pass


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


@chat.websocket('/public_chat/{user_id}/{username}')
async def public_chat(websocket: WebSocket, user_id: int, username: str, db: AsyncSession = Depends(get_session)):
    try:
        await public_manager.connect(websocket, user_id, db)
        await websocket.accept()

        while True:
            data = await websocket.receive_text()
            await public_manager.broadcast(message=data, username=username, sender_id=user_id, db=db, add_to_db=False)

    except WebSocketDisconnect:
        await public_manager.disconnect(websocket, user_id, db=db)


# @chat.websocket('/group_chat/{group_title}/{username}')
# async def group_chat(websocket: WebSocket, username: str, group_title: str, db: AsyncSession):
#     try:
#         await group_manager.connect(websocket, username)
#         ...
#     except:
#         ...


@chat.post('/create_group')
async def post_create_group(request: CreateGroupTitle, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await create_group(data=request, user_id=TOPUS.id, db=db)


@chat.post('/add_to_group')
async def post_add_to_group(request: UsersFromGroup, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await add_user_to_group(data=request, owner=TOPUS.id, db=db)


@chat.post('/kick_f_group')
async def post_kick_user(request: KickUser, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await kick_from_group(data=request, owner=TOPUS.id, db=db)


@chat.delete('/delete_group/{chat_id}')
async def post_delete_group(chat_id: int, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await delete_group(chat_id=chat_id, owner=TOPUS.id, db=db)
