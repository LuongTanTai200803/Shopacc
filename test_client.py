import socketio
import time

# Khởi tạo một client Socket.IO
sio = socketio.Client()

@sio.event
def connect():
    """Sự kiện được gọi khi kết nối thành công."""
    print("--- Đã kết nối thành công tới server! ---")
    print(">>> Bây giờ bạn có thể bắt đầu chat.")

@sio.event
def connect_error(data):
    """Sự kiện được gọi khi không thể kết nối."""
    print("!!! Kết nối thất bại! Hãy chắc chắn server backend đang chạy.")

@sio.event
def disconnect():
    """Sự kiện được gọi khi mất kết nối."""
    print("--- Đã mất kết nối với server. ---")

@sio.on('bot_reply')
def on_bot_reply(data):
    """Lắng nghe sự kiện 'bot_reply' và in ra tin nhắn của bot."""
    message = data.get('message', 'Không có tin nhắn')
    print(f"\n[BOT]: {message}\n> ", end="")

@sio.on('live_reply')
def on_live_reply(data):
    """Lắng nghe sự kiện 'live_reply' và in ra tin nhắn của admin."""
    message = data.get('message', 'Không có tin nhắn')
    print(f"\n[ADMIN]: {message}\n> ", end="")

def send_messages():
    """Vòng lặp để người dùng nhập và gửi tin nhắn."""
    print("--- Nhập 'exit' để thoát. ---")
    while True:
        message = input("> ")
        if message.lower() == 'exit':
            break
        # Gửi tin nhắn lên server với sự kiện 'user_message'
        sio.emit('user_message', {'message': message})
        time.sleep(0.1) # Đợi một chút để nhận phản hồi

if __name__ == '__main__':
    try:
        # Kết nối đến server backend đang chạy trên máy của bạn
        sio.connect('http://localhost:8000')
        
        # Bắt đầu vòng lặp gửi tin nhắn
        send_messages()
        
    except socketio.exceptions.ConnectionError as e:
        print(f"Lỗi kết nối: {e}")
    finally:
        # Ngắt kết nối khi thoát
        if sio.connected:
            sio.disconnect()
