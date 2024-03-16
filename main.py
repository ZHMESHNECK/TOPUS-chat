from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from TASKER.api.routes.auth import auth
from TASKER.api.routes.user import user
from TASKER.core.exceptions import exception
import uvicorn


topus = FastAPI()
topus.include_router(auth)
topus.include_router(user)
topus.mount('/TASKER/static', StaticFiles(directory='TASKER/static'), name='statics')



@topus.exception_handler(RequestValidationError)
async def custom_exception(requests: Request, exc: RequestValidationError):
    return await exception(requests, exc)


if __name__ == "__main__":
    uvicorn.run(topus, host="0.0.0.0", port=8000, reload=True)