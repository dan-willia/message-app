import os
import tempfile

import pytest

# add parent directory to module search path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from message_app import create_app
from message_app.db import init_db
from test_data import insert_test_data

"""
The fixtures like app, auth, client are used as arguments for test functions.
"""

@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(test_config={
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
    })

    with app.app_context():
        # set up database schema
        init_db()
        # insert testing data
        insert_test_data()

    yield app
    # everything after yield will run after the test completes
    # the code below closes the file; so each test gets a new copy of the testing database

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            json={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

