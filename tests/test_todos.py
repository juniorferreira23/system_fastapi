from http import HTTPStatus

from src.models import TodoState


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
