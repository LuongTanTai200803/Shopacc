import os
import logging
import sys
import time

from flask import Flask

from flask_migrate import upgrade
import redis
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from app.config import Config
from app.extensions import db, jwt, migratie, cache
from app.log_request import setup_request_logger
from .error_handler import register_error_handlers
from app.routes import auth_bp, acc_bp, order_bp
from flask_cors import CORS

import logging
logger = logging.getLogger(__name__) 

def create_app(config_class = Config):
    try:
        app = Flask(__name__)

        # Cấu hình CORS với nguồn gốc cụ thể
        CORS(app, resources={r"/*": {
            "origins": ["https://shopacc.up.railway.app", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }})

        app.config.from_object(config_class)

        db.init_app(app)
        jwt.init_app(app)
        migratie.init_app(app, db)
        cache.init_app(app)
        logger.error(f"CACHE_REDIS_URL: {os.getenv('CACHE_REDIS_URL')}")
        from app.models import User, Acc 
        with app.app_context():
            print("Running DB migrations...")
            upgrade()
            print("DB migrations completed.")
            
        # Đăng ký blueprint
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(acc_bp, url_prefix="/acc")
        app.register_blueprint(order_bp, url_prefix="/order")

        # Đăng ký log
        setup_request_logger(app)
        # Đăng ký error handler
        register_error_handlers(app)

        """ from app.models.user import User
        print(User.__table__.columns.keys()) """

        #print(app.config['JWT_SECRET_KEY'])

        # Không khởi tạo ở create_app()
        """     with app.app_context():
            if not os.getenv("TESTING"):
                db.drop_all()
                db.create_all() """
        # Kiểm tra endpoint
        """ with app.app_context():
            for rule in app.url_map.iter_rules():
                methods = ','.join(rule.methods)
                print(f"Endpoint: {rule.endpoint} | URL: {rule} | Methods: {methods}") """
        # # Kiểm tra kết nối Redis
        # try:
        #     r = redis.Redis.from_url(app.config['CACHE_REDIS_URL'])
        #     r.ping()
        #     logger.error("Kết nối Redis thành công!")
        # except redis.ConnectionError as e:
        #     logger.error(f"Lỗi kết nối Redis: {e}")

        # # Test kết nối Redis
        # try:
        cache.set("test_key", "test_value", timeout=60)
        logger.error(f"Cache set thành công! Giá trị: {cache.get('test_key')}")
        # except Exception as e:
        #     logger.error(f"Lỗi khi làm việc với Redis: {e}")
        @app.route('/test-cache')
        @cache.cached(timeout=60)
        def test_cache():
            print("Truy cập route /test-cache")
            logger.error("Truy cập route /test-cache")
            return "This should be cached!"

        return app
    except Exception as e:
            print("Error during app creation:", e)
            import traceback
            traceback.print_exc()
            # raise lỗi ra ngoài để Gunicorn có thể biết
            raise

def setup_logging():
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Xóa tất cả handler hiện tại
    if logger.hasHandlers():
        logger.handlers.clear()

    # Thêm StreamHandler ra stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stream_handler)

    logging.getLogger('werkzeug').setLevel(logging.WARNING)

def wait_for_db(app, db, retries=5, delay=2):
    last_exception = None

    with app.app_context():
        for i in range(retries):
            try:
                db.session.execute(text('SELECT 1'))  # test raw sql query
                print("Database is ready!")
                #db.create_all()
                break
            except OperationalError as e:
                last_exception = e
                print(f"Database not ready yet, retry {i + 1}/{retries}...")
                time.sleep(delay)
        else:
            print("Database connection failed after retries. Exiting.")
            if last_exception:
                raise last_exception
            else:
                raise Exception("Database connection failed, but no exception captured.")