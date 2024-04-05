from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from TASKER.core.security import decode_token
from TASKER.core.config import get_session
from TASKER.db.noti_db import  friend_req_noti
from typing import Dict


noti = APIRouter(prefix='/noti', tags=['Noti'])


@noti.get('/friend_req')
async def get_friend_req_noti(token: Dict = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await friend_req_noti(token=token, db=db)


# @noti.get('/chat_req')
# async def get_chat_req_noti(token: str = Depends(decode_token), db: AsyncSession = Depends(get_session)):
#     return await chat_req_noti(token=token, db=db)
