import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure logging for the Flask application."""
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter(log_format)

    # Set up logs directory
    logs_dir = os.path.join(app.instance_path, '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, 'app.log')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File handler with rotation (keeps 10 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024 * 1024,  # 1 MB per file
        backupCount=10
    )
    file_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Set Flask's logger to use the same level
    app.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Reduce noise from werkzeug in development
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

    app.logger.info(f"Logging initialized at {log_level} level")
    app.logger.info(f"Log file: {log_file}")


def get_logger(name):
    """Get a logger with the specified name."""
    return logging.getLogger(name)
