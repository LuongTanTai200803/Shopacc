import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
import logging
logger = logging.getLogger(__name__) 

redis_url = urlparse(os.getenv("CACHE_REDIS_URL"))
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI= "postgresql+psycopg2://postgres:3366@localhost:5432/db_shopacc"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'connect_timeout': 10,  # Thời gian chờ kết nối ban đầu, 10 giây
            #'read_timeout': 60, 
        },
        'pool_recycle': 7200,  # Tái sử dụng kết nối sau 2 giờ
    }
    JWT_SECRET_KEY = os.getenv("SECRET_KEY")

    CACHE_TYPE = 'RedisCache'
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL") # 0
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND") # 1
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL") # 2
    
    # CACHE_KEY_PREFIX': 'my_cache_,
    CACHE_DEFAULT_TIMEOUT = 30
    
class Testing(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:3366@localhost:5432/db_shopacc"
    TESTING = True 

class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    TESTING = False
    DEBUG = False
    CACHE_TYPE = 'RedisCache' 
    CACHE_REDIS_HOST = redis_url.hostname  
    CACHE_REDIS_PORT = redis_url.port     
    CACHE_REDIS_PASSWORD = redis_url.password  
    CACHE_REDIS_DB = redis_url.path[1:] if redis_url.path else '0'  # 2
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
    CACHE_DEFAULT_TIMEOUT = 30
    # Ghi log để debug
    logger.error(f"CACHE_REDIS_URL: {CACHE_REDIS_URL}")
    logger.error(f"CACHE_REDIS_HOST: {redis_url.hostname}")
    logger.error(f"CACHE_REDIS_PORT: {redis_url.port}")
    logger.error(f"CACHE_REDIS_DB: {redis_url.path[1:] if redis_url.path else '0'}")
    logger.error(f"CACHE_REDIS_PASSWORD: {redis_url.password}")


    