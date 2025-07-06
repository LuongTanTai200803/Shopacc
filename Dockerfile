# Sử dụng Python base image
FROM python:3.11

# Tạo thư mục app
WORKDIR /app

# Cài thêm công cụ kiểm tra mạng
RUN apt update && apt install -y net-tools iproute2
# Copy requirements và cài đặt trước
COPY requirements.txt .

# Cài đặt các thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- Dòng quan trọng được thêm vào ---
# Cài đặt các thư viện cần thiết cho SocketIO và Gunicorn
RUN pip install gevent gevent-websocket

# Copy toàn bộ project code vào container

COPY . /app

# Expose cổng ứng dụng
EXPOSE 8000

# Chạy ứng dụng bằng Gunicorn với file cấu hình
CMD ["gunicorn", "main:app", "-c", "gunicorn.conf.py"]

