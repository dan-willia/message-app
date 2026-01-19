import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')

    # Session settings
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS - comma-separated origins in env var
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

    # SocketIO logging
    SOCKETIO_LOGGER = False
    ENGINEIO_LOGGER = False

    @staticmethod
    def get_database_url(instance_path):
        """Get database URL with Render PostgreSQL compatibility."""
        database_url = os.environ.get(
            'DATABASE_URL',
            f"sqlite:///{os.path.join(instance_path, 'messenger.db')}"
        )
        # Render's PostgreSQL URLs start with 'postgres://' but SQLAlchemy 1.4+ expects 'postgresql://'
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SOCKETIO_LOGGER = True
    ENGINEIO_LOGGER = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SESSION_COOKIE_SECURE = False
    SOCKETIO_LOGGER = False
    ENGINEIO_LOGGER = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
