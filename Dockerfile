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


# Copy toàn bộ project code vào container

COPY . /app

# Expose cổng ứng dụng
EXPOSE 8000

# Đảm bảo file script có quyền thực thi
RUN chmod +x start.sh

# Chạy bằng start.sh thay vì gọi gunicorn 
CMD ["./start.sh"]
