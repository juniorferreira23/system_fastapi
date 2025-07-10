from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Todo, TodoState, User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='test', email='test@test.com', password='secret')
        session.add(user)
        await session.commit()

        db_user = await session.scalar(
            select(User).where(User.username == user.username)
        )

    assert db_user is not None
    assert asdict(db_user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'todos': [],
        'created_at': time,
        'updated_at': time,
    }


@pytest.mark.asyncio
async def test_create_todo(session: AsyncSession, user: User):
    todo = Todo(
        title='test todo',
        description='teste desc',
        state=TodoState.draft,
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    db_todo = await session.scalar(select(Todo).where(Todo.id == todo.id))

    assert db_todo is not None
    assert asdict(db_todo) == {
        'id': 1,
        'title': 'test todo',
        'description': 'teste desc',
        'state': 'draft',
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_create_todo_relationship(session: AsyncSession, user: User):
    todo = Todo(
        title='test todo',
        description='test desc',
        state=TodoState.draft,
        user_id=user.id
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    db_user = await session.scalar(select(User).where(User.id == user.id))

    assert db_user is not None
    assert db_user.todos == [todo]
