from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, Request
from TASKER.core.config import get_session, templates
from TASKER.api.schemas.users import Login, Registration
from TASKER.db.user_db import user_registration, user_login
import logging


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


@auth.get('/check')
async def check_or_create_table(db: AsyncSession = Depends(get_session)):
    try:
        async with db as session:
            result = await session.execute(text("SELECT 1"))
            result.fetchall()
        return {'status': 'OK'}
    except Exception as e:
        logging.error('user_registration-Integrity', exc_info=True)
        return JSONResponse(status_code=500, content={'status': f"Error: {str(e)}"})
