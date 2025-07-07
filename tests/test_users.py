from http import HTTPStatus

from src.schemas import UserPublic


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
    }


def test_create_user_username_already_exists_409(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username already exists'}


def test_create_user_email_already_exists_409(client, user):
    response = client.post(
        '/users',
        json={
            'username': 'test2',
            'email': 'test@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'email already exists'}


def test_read_users(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_read_user(client, user, token):
    response = client.get(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
    }


def test_update_user(client, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test2 test',
            'email': 'test2@test.com',
            'password': 'secret2',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'test2 test',
        'email': 'test2@test.com',
    }


def test_update_user_integrity_error(client, user, token):
    client.post(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test2',
            'email': 'test2@test.com',
            'password': 'secret',
        },
    )
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'test2',
            'email': 'test2@test.com',
            'password': 'secret',
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'username or email already exists'}


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'user deleted'}
