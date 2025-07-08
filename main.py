print("Main file loaded")

import os
from app import create_app, setup_logging, wait_for_db
from app.config import Production, Testing
from app.extensions import socketio, db # Import socketio và db

from alembic.command import upgrade
from alembic.config import Config as AlembicConfig


import logging
logger = logging.getLogger(__name__) 

setup_logging()
print(">>> Logging started <<<")
logging.debug("🟢 Logging setup complete.")

app = create_app(config_class=Testing)

# Chạy upgrade trước khi run app
alembic_cfg = AlembicConfig("migrations/alembic.ini")

with app.app_context():
    try:
        upgrade(alembic_cfg, "head")
        logger.debug("✅ Alembic upgrade done")
    except Exception as e:
        logger.exception("❌ Alembic upgrade failed")

if __name__ == '__main__':
    wait_for_db(app, db) # Tạm thời bỏ qua để test cho nhanh

    print(">>> Preparing to start server with error trapping...")
    try:
        # Chạy server với đầy đủ tham số
        socketio.run(app, 
                     host="0.0.0.0", 
                     port=int(os.environ.get("PORT", 8000)), 
                     debug=True)
                     
    except Exception as e:
        # Nếu có bất kỳ lỗi nào xảy ra khi khởi động, nó sẽ được in ra ở đây
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"!!! SERVER FAILED TO START: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        import traceback
        traceback.print_exc()
