from http import HTTPStatus

from jwt import decode

from src.security import create_access_token
from src.settings import Settings


def test_create_access_token():
    data = {'sub': 'test'}
    token = create_access_token(data)
    decoded = decode(token, Settings().SECRET_KEY, Settings().ALGORITHM)  # type: ignore

    assert decoded['sub'] == data['sub']
    assert 'exp' in decoded


def test_jwt_invalid_token(client, user):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': 'Bearer invalid_token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_invalid_subject_username(client):
    data = {'test': 'test'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_jwt_user_not_exists(client):
    data = {'sub': 'user_not_exists'}
    token = create_access_token(data)

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
