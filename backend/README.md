### Routes

The following routes are functioning:
- /auth/register
- /auth/login
- /contacts

Under development:
- /chat/{contact_uuid}

To do:
- /profile
- /add_contact

### Running and Testing

All of the following commands should be run while in the ```backend``` folder.

Before starting up the server you must initialize the database. Do so with
```flask --app message_app init-db```

If you commit anything to the database, you can clear it by running the command again. 

To start the server, do
```flask --app message_app run --debug```

To run the tests, do
```pytest```

You can run specific tests with, e.g,
```pytest tests/test_contacts.py```

### When running in coding.csel.io environment:

All of the following commands should be run while in the ```backend``` folder.

1. Create a virtual environment (1st time only)

```python3 -m venv .venv```

2. Activate the virtual environment

```. .venv/bin/activate```

3. Install any packages needed

```
pip install Flask
pip install -U flask-cors
pip install flask-socketio
pip install flask-login
pip install sqlalchemy
pip install pytest coverage
```

4. Run the backend code

```python3 ./run.py --debug```

5. View the backend

Using page 'chat' as an example, open the address in a new tab, filling in '<$USERNAME>' with your github user name
```https://coding.csel.io/user/<$USERNAME>/proxy/5000/chat```

6. Run tests

To run the tests, do

```pytest```

You can run specific tests with, e.g,

```pytest tests/test_chat.py```

7. Deactivate the virtual environment

```deactivate```