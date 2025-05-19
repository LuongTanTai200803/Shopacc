from app import create_app, setup_logging
from app.config import Testing

setup_logging()
app = create_app(config_class=Testing)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)