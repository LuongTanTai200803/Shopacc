print("Main file loaded")


import os
from app import create_app, setup_logging, wait_for_db
from app.config import Testing, Production, Config
from app.extensions import db

setup_logging()
app = create_app(config_class=Production)

if __name__ == '__main__':
    wait_for_db(app, db) 
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
