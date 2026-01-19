### Routes
- /auth/register
- /auth/login
- /contacts
- /chat/{contact_uuid}
- /profile
- /add_contact

### Running and Testing

All of the following commands should be run while in the ```backend``` folder.

Install dependencies.
```bash
pip install -r requirements.txt
```

Initialize the database
```bash
flask --app message_app init-db
```

Or create fake accounts if desired.
```
flask --app message_app seed-data
```

Start the server.
```bash
flask --app message_app run
```

Run all the tests.
```bash
pytest
```

Run specific tests.
```bash
pytest tests/test_contacts.py
```