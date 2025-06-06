import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI= 'sqlite:///mydb.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            #'connect_timeout': 10,  # Thời gian chờ kết nối ban đầu, 10 giây

        },
        'pool_recycle': 7200,  # Tái sử dụng kết nối sau 2 giờ
    }
    JWT_SECRET_KEY = os.getenv("SECRET_KEY")

class Testing(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:3366@localhost:5432/db_shopacc"
    TESTING = True

class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    TESTING = False
    DEBUG = False

    