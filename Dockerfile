# Sử dụng Python base image
FROM python:3.11

# Tạo thư mục app
WORKDIR /app

# Cài thêm công cụ kiểm tra mạng
RUN apt update && apt install -y net-tools iproute2

# Copy requirements và cài đặt trước
COPY requirements.txt .

# Cài đặt dependencies trước để tránh cài lại nếu code thay đổi
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ project code vào container
COPY . .

# Expose cổng ứng dụng (Railway sẽ tự động nhận diện)
EXPOSE 8000

# Chạy ứng dụng Flask với $PORT và tăng timeout

CMD ["gunicorn", "--workers", "2", "--threads", "2", "--bind", "0.0.0.0:8000", "--log-level", "debug", "-", "--error-logfile", "-", "--timeout", "120", "main:app"]