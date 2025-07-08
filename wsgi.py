from app.config import Production
from app import create_app, setup_logging
from app.extensions import socketio

import logging
logger = logging.getLogger(__name__) 

setup_logging()
app = create_app(config_class=Production)
