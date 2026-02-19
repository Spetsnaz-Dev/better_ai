from flask import Flask
from flask_cors import CORS
from .config import Config
from .logging_config import init_app_logging
from .db.models import db
from .routes.routes import main_bp
from .errors import register_error_handlers
import logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialize logging and attach middleware *after* app creation
    init_app_logging(app)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register Blueprints
    app.register_blueprint(main_bp)

    # Register Error Handlers
    register_error_handlers(app)
    
    # Log app startup
    logging.info("Application starting up")

    return app
