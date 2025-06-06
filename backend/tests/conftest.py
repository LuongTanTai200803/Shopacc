import pytest
from app import create_app  # app của bạn
from app.config import Testing
from app.extensions import db  # database của bạn


from app.models.acc import Acc
from app.models.user import User


@pytest.fixture
def app():
    app = create_app(config_class=Testing)  # mode testing
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

""" @pytest.fixture
def runner(app):
    return app.test_cli_runner()
 """
@pytest.fixture
def new_user():
    return User(username="test@example.com", password="password123")

""" @pytest.fixture
def celery_app(app):
    app.config.update(
        CELERY_TASK_ALWAYS_EAGER=True,  # Task sẽ được thực thi ngay lập tức và không cần queue
    )
    return celery

@pytest.fixture
def celery_worker(celery_app):
    return celery_app
 """
@pytest.fixture
def authenticated_client(client):
    """Đăng ký và đăng nhập, trả về client với token."""
    client.post('/auth/signup', json={
        "username": "newuser",
        "password": "password123"
    })
    login_response = client.post('/auth/login', json={
        "username": "newuser",
        "password": "password123"
    })
    access_token = login_response.json['access_token']
    client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    assert access_token is not None
    return client, access_token

@pytest.fixture(autouse=True)
def clear_posts(app):
    with app.app_context():
        yield
        Acc.query.delete()
        User.query.delete()
        db.session.commit()