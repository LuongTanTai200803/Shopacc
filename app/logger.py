import logging
import os
import requests
import json
from datetime import datetime

import logging

# Tắt log DEBUG cho requests và urllib3
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

class LokiHandler(logging.Handler):
    def __init__(self, loki_url, labels=None):
        super().__init__()
        self.loki_url = loki_url or os.getenv("LOKI_URL", "http://localhost:3100")
        self.labels = labels or {
            "app": os.getenv("APP_NAME", "flask-backend")
        }
        self.logger = logging.getLogger("loki_handler")  # logger riêng để tránh loop

    def emit(self, record):
        if record.name == "loki_handler":
            return  # tránh loop chính nó
        if record.name.startswith("geventwebsocket.handler"):
            return  # Bỏ qua hoàn toàn log này
        
        try:
            log_entry = self.format(record)
            timestamp = str(int(datetime.utcnow().timestamp() * 1e9))  # nanoseconds
            payload = {
                "streams": [
                    {
                        "stream": {"app": "flask-backend"},
                        "values": [[timestamp, log_entry]]
                    }
                ]
            }

            
            requests.post(
                url=f"{self.loki_url}/loki/api/v1/push",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=1
            )
        except Exception as e:
            print("Failed to send log to Loki:", e)

class ExcludeGeventFilter(logging.Filter):
    def filter(self, record):
        return not record.name.startswith("geventwebsocket.handler")
