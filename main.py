print("Main file loaded")


import os
from app import create_app, setup_logging, wait_for_db
from app.config import Testing, Production, Config
from app.extensions import db

from alembic.command import upgrade
from alembic.config import Config as AlembicConfig


import logging
logger = logging.getLogger(__name__) 

setup_logging()
print(">>> Logging started <<<")
logging.debug("🟢 Logging setup complete.")

app = create_app(config_class=Production)

# Chạy upgrade trước khi run app
alembic_cfg = AlembicConfig("migrations/alembic.ini")

with app.app_context():
    try:
        upgrade(alembic_cfg, "head")
        logger.debug("✅ Alembic upgrade done")
    except Exception as e:
        logger.exception("❌ Alembic upgrade failed")

if __name__ == '__main__':
    wait_for_db(app, db) 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
