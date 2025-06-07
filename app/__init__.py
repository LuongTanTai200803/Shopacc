import os
import logging
from flask import Flask
from flask_migrate import upgrade
from app.config import Config
from app.extensions import db, jwt, migratie
from app.log_request import setup_request_logger
from .error_handler import register_error_handlers
from app.routes import auth_bp, acc_bp, order_bp
from flask_cors import CORS


def create_app(config_class = Config):
    app = Flask(__name__)

    # Cấu hình CORS với nguồn gốc cụ thể
    CORS(app, resources={r"/*": {
        "origins": ["https://shopacc22222-production.up.railway.app"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }})

    app.config.from_object(config_class)

    db.init_app(app)
    jwt.init_app(app)
    migratie.init_app(app, db)

    from app.models import User, Acc 
    with app.app_context():
        # Tự động chạy migration
        upgrade()
        
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

    return app

def setup_logging():
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Cấu hình log
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[logging.StreamHandler()]
    ) 

    werkzeug_log = logging.getLogger('werkzeug')
    werkzeug_log.setLevel(logging.CRITICAL)
    #werkzeug_log.propagate = False 
