from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from TASKER.core.security import decode_token
from TASKER.core.config import get_session
from TASKER.api.schemas.users import UserFToken
from TASKER.db.noti_db import friend_req_noti, mess_req_noti


noti = APIRouter(prefix='/noti', tags=['Noti'])


@noti.get('/friend_req')
async def get_friend_req_noti(token: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await friend_req_noti(token=token, db=db)


@noti.get('/mess_noti')
async def get_chat_req_noti(token: str = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await mess_req_noti(token=token, db=db)
