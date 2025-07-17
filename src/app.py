import asyncio
import sys
from http import HTTPStatus

from fastapi import FastAPI

from src.routers import auth, todos, users

if sys.platform == 'win32':  # pragma: no cover
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)


@app.get('/', status_code=HTTPStatus.OK)
async def read_root():
    return {'message': 'Hello world!'}
