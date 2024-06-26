from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from TASKER.api.schemas.utils import SearchRequest
from TASKER.api.schemas.users import UserFToken
from TASKER.core.security import decode_token
from TASKER.core.config import get_session
from TASKER.db.user_db import get_search

search = APIRouter(prefix='/search', tags=['Search'])


@search.post('/')
async def req_search(request: SearchRequest, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    return await get_search(data=request, token=TOPUS, db=db)
