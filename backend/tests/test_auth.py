import pytest
from flask import g, session
from message_app import db_
from flask_login import current_user

from message_app.data_classes import User

def test_register(client, app):
    response = client.post(
        '/auth/register', json={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert 'success' in response.json['status']

    with app.app_context():
        user = db_.session.query(User).filter_by(user_name='a').first()
        assert user is not None

@pytest.mark.parametrize(('username', 'password', 'status_code', 'message'), (
    ('', '', 200, 'Username is required.'),
    ('a', '', 200, 'Password is required.'),
    ('test', 'test', 200, 'test is not available')
))
def test_register_validate_input(client, username, password, status_code, message):
    response = client.post(
        '/auth/register',
        json={'username': username, 'password': password}
    )
    assert response.status_code == status_code
    assert message in response.json['error']

def test_login(client, auth):
    auth.login()
    with client:
        client.get('/contacts')
        assert current_user.id == 1
        assert current_user.user_name == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('test', 'test', b'success'),
    ('test', 'test', b'test'),
    ('test', 'test', b'uuid'),
    ('a', 'test', b'Credentials not valid.'),
    ('test', 'a', b'Credentials not valid.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_get_current_user(auth, client):
    response = client.get('/auth/current-user')
    assert response.status_code == 302
    auth.login()
    response = client.get('/auth/current-user')
    assert response.status_code == 200
    assert b'test' in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


