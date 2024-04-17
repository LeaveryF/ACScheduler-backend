import pytest
from flask import g, session


def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/acadmin/rooms"

    with client:
        client.get('/')
        assert session['user_id'] == 2
        assert g.user.username == 'acadmin'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('test', 'acadmin', b'Incorrect username.'),
    ('acadmin', 'test', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
