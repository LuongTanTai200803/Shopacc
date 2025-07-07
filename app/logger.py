import logging
import os
import requests
import json
from datetime import datetime

class LokiHandler(logging.Handler):
    def emit(self, record):
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

            loki_host = os.getenv("LOKI_URL", "http://<YOUR_EC2_PUBLIC_IP>:3100")
            requests.post(
                url=f"{loki_host}/loki/api/v1/push",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=1
            )
        except Exception as e:
            print("Failed to send log to Loki:", e)
