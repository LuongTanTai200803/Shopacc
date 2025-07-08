import os
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_socketio import SocketIO
redis_url = os.environ.get('CACHE_REDIS_URL')
print(f"DEBUG: Redis URL from environment is: {redis_url}")
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate() 
cache = Cache()

socketio = SocketIO(async_mode='gevent', message_queue=redis_url)
