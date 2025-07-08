### WebSocket Support

- Dùng `gunicorn wsgi:app -c gunicorn.conf.py`
- Đảm bảo `worker_class = geventwebsocket.gunicorn.workers.GeventWebSocketWorker`
- Frontend phải khởi tạo socket với `transports: ['websocket']`