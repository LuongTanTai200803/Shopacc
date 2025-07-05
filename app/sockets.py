import re
from flask import request
from .extensions import socketio
from .models import Acc  # Import model Acc để truy vấn database
from sqlalchemy import func
from flask_socketio import emit

# Dictionary để quản lý các cuộc trò chuyện đang cần admin hỗ trợ
live_chat_queue = {}

@socketio.on('connect')
def handle_connect():
    """Sự kiện khi một người dùng kết nối vào chat."""
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Sự kiện khi người dùng ngắt kết nối."""
    print(f"Client disconnected: {request.sid}")
    if request.sid in live_chat_queue:
        del live_chat_queue[request.sid]
        socketio.emit('livechat_user_left', {'sid': request.sid})

@socketio.on('user_message')
def handle_user_message(data):
    """
    Nhận tin nhắn từ người dùng và cho chatbot xử lý.
    Đây là bộ não chính của chatbot.
    """
    user_message = data.get('message', '').lower()
    user_sid = request.sid

    # --- Ưu tiên 1: Chào hỏi & FAQ ---
    if any(word in user_message for word in ["chào", "hello", "hi"]):
        bot_response = "Bot: Chào bạn, tôi là trợ lý ảo của ShopACC. Tôi có thể giúp gì cho bạn?"
        emit('bot_reply', {'message': bot_response}, room=user_sid)
        return

    if any(word in user_message for word in ["mua", "thanh toán"]):
        bot_response = "Bot: Để mua tài khoản, bạn chỉ cần nhấn nút 'Xem chi tiết' và sau đó chọn 'Mua ngay'. Hệ thống sẽ hướng dẫn bạn các bước thanh toán."
        emit('bot_reply', {'message': bot_response}, room=user_sid)
        return

    if "uy tín" in user_message:
        bot_response = "Bot: ShopACC cam kết uy tín 100%, với chính sách bảo hành rõ ràng và hỗ trợ khách hàng nhanh chóng. Bạn có thể yên tâm giao dịch."
        emit('bot_reply', {'message': bot_response}, room=user_sid)
        return

    if "bảo hành" in user_message:
        bot_response = "Bot: Shop có chính sách bảo hành 1 đổi 1 trong vòng 7 ngày nếu tài khoản có lỗi phát sinh từ phía shop. Vui lòng liên hệ nhân viên hỗ trợ để được giúp đỡ."
        emit('bot_reply', {'message': bot_response}, room=user_sid)
        return

    # --- Ưu tiên 2: Tìm kiếm và truy vấn thông tin ---
    numbers = re.findall(r'\d+', user_message)
    
    # Tìm tài khoản theo ID
    if ("chi tiết" in user_message or "thông tin" in user_message) and numbers:
        try:
            acc_id = int(numbers[0])
            account = Acc.query.get(acc_id)
            if account:
                bot_response = f"Bot: Thông tin tài khoản ID {acc_id}:\n- Tướng: {account.hero}\n- Skin: {account.skin}\n- Giá: {account.price:,.0f} VNĐ."
            else:
                bot_response = f"Bot: Rất tiếc, tôi không tìm thấy tài khoản nào có ID là {acc_id}."
            emit('bot_reply', {'message': bot_response}, room=user_sid)
            return
        except (ValueError, IndexError):
            pass

    # Tìm kiếm tài khoản theo tiêu chí
    if any(word in user_message for word in ["tìm", "kiếm", "có acc", "acc giá", "acc có"]):
        query = Acc.query
        filters_applied = []

        if "skin" in user_message and numbers:
            skin_count = int(numbers[0])
            query = query.filter(Acc.skin >= skin_count)
            filters_applied.append(f"có từ {skin_count} skin")
        
        if "tướng" in user_message or "hero" in user_message and numbers:
            hero_count = int(numbers[0])
            query = query.filter(Acc.hero >= hero_count)
            filters_applied.append(f"có từ {hero_count} tướng")

        if ("giá dưới" in user_message or "giá nhỏ hơn" in user_message) and numbers:
            price_limit = int(numbers[0])
            query = query.filter(Acc.price <= price_limit)
            filters_applied.append(f"giá dưới {price_limit:,.0f} VNĐ")

        results = query.limit(3).all()

        if results:
            criteria_str = " và ".join(filters_applied)
            bot_response = f"Bot: Tôi tìm thấy vài tài khoản phù hợp với tiêu chí ({criteria_str}):\n"
            for acc in results:
                bot_response += f"- ID: {acc.id}, Giá: {acc.price:,.0f}, Skin: {acc.skin}, Tướng: {acc.hero}\n"
        else:
            bot_response = "Bot: Rất tiếc, không có tài khoản nào phù hợp với yêu cầu của bạn."
            
        emit('bot_reply', {'message': bot_response}, room=user_sid)
        return

    # --- Ưu tiên 3: Yêu cầu gặp nhân viên hoặc các câu hỏi khác ---
    if any(word in user_message for word in ["nhân viên", "người", "admin", "hỗ trợ", "tư vấn"]):
        bot_response = "Bot: Vui lòng chờ trong giây lát, tôi sẽ kết nối bạn với nhân viên hỗ trợ."
    else:
        # Nếu không có quy tắc nào khớp, mặc định chuyển cho admin
        bot_response = "Bot: Tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng chờ để được kết nối với nhân viên hỗ trợ."

    # Gửi tin nhắn chờ cho người dùng và gửi yêu cầu cho admin
    emit('bot_reply', {'message': bot_response}, room=user_sid)
    if user_sid not in live_chat_queue:
        live_chat_queue[user_sid] = user_message
        socketio.emit('livechat_request', {'sid': user_sid, 'message': data.get('message')})

@socketio.on('admin_message')
def handle_admin_message(data):
    """Nhận tin nhắn từ admin và gửi cho người dùng cụ thể."""
    target_user_sid = data.get('sid')
    admin_msg = data.get('message')
    
    if target_user_sid in live_chat_queue:
        del live_chat_queue[target_user_sid]

    emit('live_reply', {'message': f"Admin: {admin_msg}"}, room=target_user_sid)