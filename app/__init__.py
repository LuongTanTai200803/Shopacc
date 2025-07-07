from logging.handlers import RotatingFileHandler
import os
import logging
import sys
import time
import redis

from flask import Flask
from flask_migrate import upgrade
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .logger import LokiHandler

from .config import Config
from .extensions import db, jwt, migrate, cache, socketio
from .log_request import setup_request_logger

from .error_handler import register_error_handlers
from .routes import auth_bp, acc_bp, order_bp
from flask_cors import CORS


from . import sockets 

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from prometheus_flask_exporter import PrometheusMetrics
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration



import logging
logger = logging.getLogger("flask.app")

def create_app(config_class = Config):
    try:
        app = Flask(__name__)

        # Khởi tạo metric
        REQUEST_COUNT = Counter("http_requests_total", "Total HTTP Requests", ["method", "endpoint"])

        # Cấu hình CORS với nguồn gốc cụ thể
        CORS(app, resources={r"/*": {
            "origins": ["https://shopacc.up.railway.app", "http://localhost:5173"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }})

        app.config.from_object(config_class)

        sentry_sdk.init(
        dsn="https://fdc26a8a1a22a4a0e58400fec27e878b@o4509087854559232.ingest.us.sentry.io/4509598772035584",  # thay bằng DSN thật
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment="production"  # hoặc "development" nếu đang dev
        )
        metrics = PrometheusMetrics(app)
        db.init_app(app)
        jwt.init_app(app)
        migrate.init_app(app, db, directory="./migrations")
        cache.init_app(app)

        # Khởi tạo SocketIO với app và cấu hình CORS cho nó
        socketio.init_app(app, cors_allowed_origins=["https://shopacc.up.railway.app", "http://localhost:5173"])

        from app.models import User, Acc 
        with app.app_context():
            print("Running DB migrations...")
            upgrade()
            print("DB migrations completed.")
            


        logger.debug(f"CACHE_REDIS_URL: {os.getenv('CACHE_REDIS_URL')}")

        from .models import User, Acc 

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
        # with app.app_context():
        #     try:
        #         r = redis.Redis.from_url(app.config['CACHE_REDIS_URL'])
        #         r.ping()
        #         logger.error("Kết nối Redis thành công!")
        #     except Exception as e:
        #         logger.error(f"Lỗi kết nối Redis: {e}")

        # # Test kết nối Redis
        # try:
        # cache.set("test_key", "test_value", timeout=60)



        # except Exception as e:
        #     logger.error(f"Lỗi khi làm việc với Redis: {e}")
        @app.route("/error-redis")
        def test_redis_error():
            r = redis.StrictRedis.from_url("redis://localhost:6379/2")
            # Force lỗi (ví dụ Redis không kết nối được)
            r.get("force-error")  # Nếu Redis fail, sẽ tự raise lỗi lên Sentry
            return "OK"
        
        @app.route("/error")
        def trigger_error():
            1 / 0  # gây lỗi chia cho 0 để Sentry bắt được

        # Thêm route /metrics 
        @app.route("/metrics")
        def metrics():
            REQUEST_COUNT.labels(method="GET", endpoint="/auth/ping").inc()
            return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

        return app
    except Exception as e:
            print("Error during app creation:", e)
            import traceback
            traceback.print_exc()
            # raise lỗi ra ngoài để Gunicorn có thể biết
            raise


def setup_logging():
    log_level = logging.DEBUG if os.getenv("FLASK_ENV") == "development" else logging.INFO

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    # Đảm bảo file tồn tại trước khi Promtail đọc
    if not os.path.exists(log_file):
        with open(log_file, 'w'): pass
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Xóa tất cả handler hiện tại
    if logger.hasHandlers():
        logger.handlers.clear()

    # 1. Ghi ra terminal
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(stream_handler)
    
    # 2. Ghi ra file
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10_000_000, backupCount=3)
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # 3. Ghi log từ Flask
    flask_logger = logging.getLogger('flask.app')
    flask_logger.setLevel(logging.DEBUG)
    flask_logger.addHandler(file_handler)

    loki_url = os.getenv("LOKI_URL", "http://localhost:3100")

    # Loki HTTP
    loki_handler = LokiHandler(loki_url=loki_url)
    loki_handler.setLevel(logging.INFO)
    loki_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(loki_handler)

    logging.getLogger('werkzeug').setLevel(logging.INFO)


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
