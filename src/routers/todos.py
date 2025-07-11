from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.models import Todo, User
from src.schemas import FilterTodo, TodoList, TodoPublic, TodoSchema
from src.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

SessionAnnotated = Annotated[AsyncSession, Depends(get_session)]
CurrentUserAnnotated = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema, session: SessionAnnotated, user: CurrentUserAnnotated
):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)

    return new_todo


@router.get('/', status_code=HTTPStatus.OK, response_model=TodoList)
async def read_todos(
    todo_filter: Annotated[FilterTodo, Query()],
    session: SessionAnnotated,
    user: CurrentUserAnnotated,
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state.contains(todo_filter.state))

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}
