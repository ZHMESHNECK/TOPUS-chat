from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Request
from TASKER.core.config import get_session, templates
from TASKER.api.schemas.users import Login, Registration
from TASKER.db.user_db import user_registration, user_login


auth = APIRouter(prefix='/auth', tags=['Authentication'])


@auth.get('/login')
async def login(request: Request):
    return templates.TemplateResponse('login_reg.html', {'request': request})


@auth.post('/login')
async def login(data: Login, db: AsyncSession = Depends(get_session)):
    return await user_login(data, db)


@auth.post('/registration')
async def registration(data: Registration, db: AsyncSession = Depends(get_session)):
    return await user_registration(data, db)
