from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from TASKER.core.security import decode_token
from TASKER.core.config import get_session
from TASKER.api.schemas.users import UserFToken
from TASKER.db.user_db import declain_friend_request, user_send_request_friend, accept_friend_request, delete_friendship


user = APIRouter(prefix='/user', tags=['User'])


@user.get('/add_friend/{friend_id}')
async def send_friend_req(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await user_send_request_friend(token.id, friend_id, db)


@user.get('/accept_friend/{friend_id}')
async def accept_friend_req(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await accept_friend_request(token.id, friend_id, db)


@user.get('/declain_friend/{friend_id}')
async def declain_friend_req(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await declain_friend_request(token.id, friend_id, db)


@user.delete('/del_friend/{friend_id}')
async def delete_friend_req(friend_id: int, token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await delete_friendship(token.id, friend_id, db)
