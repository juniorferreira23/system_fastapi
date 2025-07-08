from dataclasses import asdict

import pytest
from sqlalchemy import select

from src.models import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='test', email='test@test.com', password='secret'
        )
        session.add(new_user)
        await session.commit()

        db_user = await session.scalar(
            select(User).where(User.username == 'test')
        )

    assert asdict(db_user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }
