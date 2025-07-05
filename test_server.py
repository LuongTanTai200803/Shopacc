
# test_server.py
from flask import Flask
from flask_socketio import SocketIO

# Khởi tạo một app Flask siêu đơn giản
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-testing'

# Khởi tạo SocketIO và buộc nó dùng 'gevent'
socketio = SocketIO(app, async_mode='gevent')

@app.route('/')
def index():
    return '<h1>Minimal Test Server is Running!</h1>'

@socketio.on('connect')
def handle_test_connect():
    print('>>> A client connected successfully! <<<')

if __name__ == '__main__':
    print('--- Attempting to start MINIMAL test server on port 8000... ---')
    try:
        socketio.run(app, host='0.0.0.0', port=8022)
    except Exception as e:
        print(f"!!! MINIMAL SERVER FAILED: {e}")
        import traceback
        traceback.print_exc()