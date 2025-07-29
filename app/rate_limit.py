

import time
from flask import jsonify, request


request_logs= {}

RATE_LIMIT = 10  # Giới hạn số lượng request
TIME_WINDOW = 5  # Thời gian tính bằng giây
BURST =20  # Số lượng request tối đa trong một khoảng thời gian ngắn

def setup_rate_limit(app):
    @app.before_request
    def middleware():
        ip = request.remote_addr
        now = time.time()

        if ip not in request_logs:
            request_logs[ip] = []

        # Lấy log của IP trong khoảng thời gian gần nhất
        recent_requests = [t for t in request_logs[ip] if now - t < TIME_WINDOW]
        request_logs[ip] = recent_requests
        print(f"IP: {ip} - Recent requests: {len(recent_requests)}")
        if len(recent_requests) >= (RATE_LIMIT + BURST):
            return jsonify({"error": "Too many requests"}), 429

        request_logs[ip].append(now)
    