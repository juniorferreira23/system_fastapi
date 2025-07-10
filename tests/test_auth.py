from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'Bearer'


def test_login_for_access_token_not_found_user(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'test', 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'incorrect username or password'}


def test_login_for_access_token_with_wrong_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'test'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'incorrect username or password'}


def test_token_expired_after_time(client, user):
    with freeze_time('2025-07-09 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-09 12:32:00'):
        response = client.delete(
            '/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_expired_dont_refresh(client, user):
    with freeze_time('2025-07-09 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-09 12:32:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, user):
    with freeze_time('2025-07-09 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.username, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-07-09 12:29:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        token = response.json()

        assert response.status_code == HTTPStatus.OK
        assert 'access_token' in token
        assert token['token_type'] == 'Bearer'
