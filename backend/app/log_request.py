import time
import logging
from flask import request

def setup_request_logger(app):
    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def log_response(response):
        if not hasattr(request, "start_time"):
            return response

        duration = time.time() - request.start_time
        duration_ms = int(duration * 1000)

        method = request.method
        path = request.path
        status = response.status_code
        ip = request.remote_addr
        user_id = None

        try:
            from flask_jwt_extended import get_jwt_identity
            user_id = get_jwt_identity()
        except Exception:
            pass

        log_params = {
            "method": method,
            "path": path,
            "status": status,
            "duration": duration_ms,
            "ip": ip,
            "user": user_id,
        }

        log_message = (
            f"{log_params['method']} {log_params['path']} "
            f"{log_params['status']} {log_params['duration']}ms "
            f"IP:{log_params['ip']} User:{log_params['user']}"
        )

        if status >= 500:
            logging.error(log_message)
        elif status >= 400:
            logging.warning(log_message)
        else:
            logging.info(log_message)

        return response