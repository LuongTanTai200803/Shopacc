import multiprocessing
import sys

bind = "0.0.0.0:8000"
workers = 2
worker_class = 'geventwebsocket.gunicorn.workers.GeventWebSocketWorker'
threads = 2
timeout = 120
loglevel = "debug"

# Logging config
accesslog = "-"     # "-" nghĩa là log ra stdout
errorlog = "-"      # log lỗi ra stderr
capture_output = True  # ghi stdout/stderr từ app
