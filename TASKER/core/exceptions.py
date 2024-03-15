from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import Request


async def exception(requests: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        if len(error.get('loc')) > 1:
            errors[error.get('loc')[1]] = error.get('msg').split('Value error, ')[1]

    return JSONResponse(content=(errors, 'Невідома помилка')[len(errors) < 1], status_code=400)
