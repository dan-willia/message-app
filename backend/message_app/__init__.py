import logging
import os

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

from .config import config, DevelopmentConfig
from .logger import setup_logging, get_logger

# Module-level logger (available before app context)
logger = get_logger(__name__)

# Create instance of SocketIO: not yet bound to any Flask app
# server attribute is None b/c there is no app to serve
# Note: cors_allowed_origins will be updated in create_app based on config
socketio = SocketIO()
db_ = SQLAlchemy()

def create_app(test_config=None, config_name=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Determine which config to use
    if test_config is not None:
        # Testing: use provided test config dict
        app_config = config['testing']
        app.config.from_object(app_config)
        app.config.from_mapping(test_config)
    else:
        # Use config_name or default to environment variable or 'development'
        config_name = config_name or os.environ.get('FLASK_ENV', 'development')
        app_config = config.get(config_name, config['default'])
        app.config.from_object(app_config)
        # Load instance config if it exists
        app.config.from_pyfile('config.py', silent=True)

    # Initialize logging
    setup_logging(app)
    app.logger.debug(f"Flask app created with config: {config_name or 'testing'}")

    # Set database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = app_config.get_database_url(app.instance_path)

    db_.init_app(app)
    app.logger.debug("SQLAlchemy initialized")

    # Initialize SocketIO with config values
    socketio.init_app(
        app,
        logger=app.config.get('SOCKETIO_LOGGER', False),
        engineio_logger=app.config.get('ENGINEIO_LOGGER', False),
        cors_allowed_origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173'])
    )
    app.logger.debug("SocketIO initialized")

    # Allow requests from React
    CORS(app, supports_credentials=True, origins=app.config.get('CORS_ORIGINS', ['http://localhost:5173']))
    # print("CORS configured")

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        from .data_classes import User
        from . import db_
        return db_.session.scalar(select(User).where(User.id == int(user_id)))

    # print("App config" + str(app.config))

    from . import db
    db.init_app(app)

    from . import seed_demo
    seed_demo.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import contacts
    app.register_blueprint(contacts.bp)

    from . import chat
    app.register_blueprint(chat.bp)
    
    from . import usersearch
    app.register_blueprint(usersearch.bp)
    
    return app

if __name__ == '__main__':
    # Alternative way to run the app - creates a single SocketIO instance
    # Prefer using: flask --app message_app run

    app = create_app()
    # Starts server that can handle BOTH HTTP requests and WebSocket connections
    #  - sets socketio.server
    #  - begins listening for connections
    #  - blocks and runs the event loop
    socketio.run(app, debug=True)
