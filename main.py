from app import create_app, setup_logging
from app.config import Testing, Production

setup_logging()
app = create_app(config_class=Production)

if __name__ == '__main__':
    app.run(debug=False)