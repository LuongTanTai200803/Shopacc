#!/bin/bash

set -e  # Dừng script nếu có bất kỳ lỗi nào

echo "🚀 Khởi động Gunicorn server..."
exec gunicorn wsgi:app -c gunicorn.conf.py

echo "⏳ Đợi DB sẵn sàng..."
python scripts/wait_for_db.py

echo "🧱 Chạy Alembic migrations..."
python scripts/upgrade_db.py

echo "🛠️ Cấu hình logging..."
python scripts/setup_logging.py


