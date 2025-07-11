from http import HTTPStatus

import factory
import factory.fuzzy
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Todo, TodoState, User


class TodoFactory(factory.base.Factory):
    class Meta:  # type: ignore
        model = Todo

    title = factory.faker.Faker('text')
    description = factory.faker.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


def test_create_todo(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test title',
            'description': 'test desc',
            'state': TodoState.draft,
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'test title',
        'description': 'test desc',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_read_todos(session: AsyncSession, user: User, client, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(expected_todos, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_pagination(
    session: AsyncSession, user: User, client, token
):
    expected_todos = 2
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offiset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_by_title_filter(
    session: AsyncSession, user: User, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, title='title todo 1'
        )
    )
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, title='title todo 2')
    )
    await session.commit()

    response = client.get(
        '/todos/?title=title todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_by_description_filter(
    session: AsyncSession, user: User, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, description='desc todo 1'
        )
    )
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, title='title todo 2')
    )
    await session.commit()

    response = client.get(
        '/todos/?description=desc todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_by_state_filter(
    session: AsyncSession, user: User, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos, user_id=user.id, state=TodoState.todo
        )
    )
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, state=TodoState.done)
    )
    await session.commit()

    response = client.get(
        '/todos/?state=todo', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_read_todos_combination_filters(
    session: AsyncSession, user: User, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            expected_todos,
            user_id=user.id,
            title='test title',
            description='test desc',
            state=TodoState.todo,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            2,
            user_id=user.id,
            title='other todo',
            description='other desc',
            state=TodoState.done,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=test title&description=test desc&state=todo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_update_todo(client, user: User, session: AsyncSession, token):
    todo = Todo(
        title='test todo',
        description='test desc',
        state=TodoState.todo,
        user_id=user.id
    )

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test2 todo2',
            'description': 'test2 desc2',
            'state': 'todo'
        }
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'title': 'test2 todo2',
        'description': 'test2 desc2',
        'state': 'todo'
    }


@pytest.mark.asyncio
async def test_update_todo_not_found(client, user: User, token):
    response = client.patch(
        '/todos/10',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'test2 todo2',
            'description': 'test2 desc2',
            'state': 'todo'
        }
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'task not found'}
