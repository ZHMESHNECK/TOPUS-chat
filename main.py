from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse
from fastapi import Depends, FastAPI, Request
from TASKER.core.exceptions import exception
from TASKER.core.security import decode_token
from TASKER.core.config import get_session, templates
from TASKER.api.schemas.users import UserFToken
from TASKER.api.routes.notification import noti
from TASKER.api.routes.search import search
from TASKER.api.routes.chat import chat
from TASKER.api.routes.auth import auth
from TASKER.api.routes.user import user
from TASKER.db.noti_db import get_count_notification
from TASKER.db.user_db import get_list_friends, logout
import uvicorn


topus = FastAPI()
topus.include_router(auth)
topus.include_router(user)
topus.include_router(chat)
topus.include_router(search)
topus.include_router(noti)
topus.mount('/TASKER/static',
            StaticFiles(directory='TASKER/static'), name='statics')


@topus.exception_handler(RequestValidationError)
async def custom_exception(requests: Request, exc: RequestValidationError):
    return await exception(requests, exc)


@topus.get('/')
async def main(request: Request, TOPUS: UserFToken = Depends(decode_token), db: AsyncSession = Depends(get_session)):
    if not TOPUS:
        return RedirectResponse(url='auth/login')
    list_friends = await get_list_friends(TOPUS, db)
    notifications = await get_count_notification(TOPUS, db)

    user = {
        'id': TOPUS.id,
        'username': TOPUS.username
    }
    return templates.TemplateResponse('main.html', {'request': request, 'user': user, 'friends': list_friends, 'notifications': notifications})


@topus.post('/logout')
async def get_logout(request: Request, TOPUS: UserFToken = Depends(decode_token)):
    return await logout(request)

if __name__ == "__main__":
    uvicorn.run(topus, host="0.0.0.0", port=8000, reload=True)
