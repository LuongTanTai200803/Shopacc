import re
import random
import json
import os
from flask import request
from .extensions import socketio
from .models import Acc
from sqlalchemy import func
from flask_socketio import emit
import google.generativeai as genai

# --- PHẦN CẤU HÌNH VÀ TẢI DỮ LIỆU (Giữ nguyên) ---
live_chat_queue = {}

try:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("!!! CẢNH BÁO: Không tìm thấy GEMINI_API_KEY. Chức năng AI sẽ bị vô hiệu hóa. !!!")
        gemini_model = None
    else:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"!!! LỖI: Không thể khởi tạo Gemini: {e} !!!")
    gemini_model = None

def load_intents():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, 'intents.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)["intents"]
    except FileNotFoundError:
        print("!!! LỖI: Không tìm thấy file intents.json !!!")
        return []

JSON_INTENTS = load_intents()

# --- NÂNG CẤP: HÀM XỬ LÝ SỐ THÔNG MINH HƠN ---
def parse_price_from_message(message):
    """Trích xuất giá tiền từ tin nhắn, hiểu được 'k' (ngàn) và 'm' (triệu)."""
    match_m = re.search(r'(\d+\.?\d*)\s*m\b', message)
    if match_m:
        price = float(match_m.group(1)) * 1_000_000
        return int(price)
    match_k = re.search(r'(\d+\.?\d*)\s*k\b', message)
    if match_k:
        price = float(match_k.group(1)) * 1_000
        return int(price)
    numbers = re.findall(r'\d+', message)
    if numbers:
        return max(int(num) for num in numbers)
    return None

# --- NÂNG CẤP: HÀM GỌI AI VỚI NHIỀU NHIỆM VỤ ---
def ask_gemini_ai(task, user_message=None, context=None):
    """
    Hàm gọi AI đa năng:
    - task='answer': Trả lời câu hỏi của người dùng.
    - task='rephrase': Diễn đạt lại một câu văn cho hay hơn.
    """
    if not gemini_model:
        return None

    # "Bộ não" của AI được nâng cấp tại đây
    system_prompt = ""
    if task == 'answer':
        system_prompt = """
        Bạn là một trợ lý ảo tên là Bot, làm việc cho một cửa hàng bán tài khoản game Liên Minh Huyền Thoại (LMHT) tên là ShopACC.
        Nhiệm vụ của bạn là trả lời các câu hỏi của khách hàng một cách thân thiện, chuyên nghiệp và chỉ tập trung vào các chủ đề liên quan đến shop.
        QUY TẮC VÀNG:
        1. BẠN CHỈ BÁN ACC LMHT.
        2. Khi tư vấn, hãy dựa vào dữ liệu tài khoản được cung cấp để đưa ra gợi ý.
        3. Nếu người dùng hỏi một câu không liên quan đến cửa hàng game, bạn PHẢI từ chối trả lời một cách lịch sự.
        """
        if context:
            system_prompt += f"\n\nDỮ LIỆU THAM KHẢO:\n{context}"
        content_to_send = f"{system_prompt}\n\nCâu hỏi của khách hàng: '{user_message}'"

    elif task == 'rephrase':
        system_prompt = """
        Bạn là một trợ lý ảo bán hàng game thân thiện. Hãy diễn đạt lại câu văn sau đây sao cho tự nhiên, gần gũi và chuyên nghiệp hơn, nhưng phải giữ nguyên ý nghĩa cốt lõi của nó. Không thêm thông tin mới.
        """
        content_to_send = f"{system_prompt}\n\nCâu văn cần diễn đạt lại: '{context}'"
    
    else:
        return None

    try:
        response = gemini_model.generate_content(content_to_send)
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi Gemini API: {e}")
        return "Bot: Rất xin lỗi, hiện tại tôi không thể kết nối với bộ não AI của mình. Vui lòng thử lại sau."

# --- CÁC HÀM XỬ LÝ PHỨC TẠP ---
def handle_account_details(user_message, numbers):
    # ... (Giữ nguyên)
    if not numbers: return None
    try:
        acc_id = int(numbers[0])
        account = Acc.query.get(acc_id)
        if account:
            return f"Bot: Thông tin tài khoản ID {acc_id}:\n- Tướng: {account.hero}\n- Skin: {account.skin}\n- Giá: {account.price:,.0f} VNĐ."
        return f"Bot: Rất tiếc, không tìm thấy tài khoản nào có ID là {acc_id}."
    except (ValueError, IndexError):
        return "Bot: ID tài khoản không hợp lệ."

def handle_consultation(user_message, numbers):
    # ... (Giữ nguyên)
    price_limit = parse_price_from_message(user_message)
    if not price_limit:
        return ask_gemini_ai(task='answer', user_message=user_message)
    accounts = Acc.query.filter(Acc.price <= price_limit).order_by(Acc.price.desc()).limit(5).all()
    if not accounts:
        return f"Bot: Rất tiếc, hiện tại shop không có tài khoản nào trong tầm giá {price_limit:,.0f} VNĐ."
    context_for_ai = "Dưới đây là một vài tài khoản LMHT có giá dưới hoặc bằng " \
                     f"{price_limit:,.0f} VNĐ. Hãy dựa vào đây để tư vấn cho khách:\n"
    for acc in accounts:
        context_for_ai += f"- ID {acc.id}: Giá {acc.price:,.0f}, có {acc.hero} tướng, {acc.skin} skin.\n"
    return ask_gemini_ai(task='answer', user_message=user_message, context=context_for_ai)

COMPLEX_HANDLERS = [
    {"keywords": ["chi tiết", "thông tin", "xem acc"], "handler": handle_account_details},
    {"keywords": ["tư vấn", "gợi ý", "nên mua"], "handler": handle_consultation},
]

# --- PHẦN XỬ LÝ SỰ KIỆN SOCKETIO ---
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    if request.sid in live_chat_queue:
        del live_chat_queue[request.sid]
        socketio.emit('livechat_user_left', {'sid': request.sid})

@socketio.on('user_message')
def handle_user_message(data):
    user_message = data.get('message', '').lower()
    original_message = data.get('message', '')
    user_sid = request.sid
    numbers = re.findall(r'\d+', user_message)

    # 1. Ưu tiên xử lý các câu hỏi đơn giản từ file JSON, sau đó nhờ AI diễn đạt lại
    for intent in JSON_INTENTS:
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', user_message) for keyword in intent["keywords"]):
            # Chọn ngẫu nhiên một câu trả lời gốc
            base_response = random.choice(intent["responses"])
            # Nhờ AI diễn đạt lại cho hay hơn
            final_response = ask_gemini_ai(task='rephrase', context=base_response)
            emit('bot_reply', {'message': final_response or base_response}, room=user_sid)
            return

    # 2. Xử lý các chức năng phức tạp
    for intent in COMPLEX_HANDLERS:
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', user_message) for keyword in intent["keywords"]):
            response = intent["handler"](user_message, numbers)
            if response:
                emit('bot_reply', {'message': response}, room=user_sid)
                return

    # 3. Nếu không khớp, hỏi AI chung chung
    ai_response = ask_gemini_ai(task='answer', user_message=original_message)
    if ai_response:
        emit('bot_reply', {'message': ai_response}, room=user_sid)
        return

    # 4. Nếu AI cũng không xử lý được, chuyển cho admin
    fallback_to_live_chat(user_sid, original_message)

def fallback_to_live_chat(user_sid, original_message):
    if user_sid not in live_chat_queue:
        live_chat_queue[user_sid] = original_message
        bot_response = "Bot: Tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng chờ để được kết nối với nhân viên hỗ trợ."
    else:
        bot_response = "Bot: Nhân viên hỗ trợ sẽ trả lời bạn ngay. Vui lòng chờ một chút."
    
    emit('bot_reply', {'message': bot_response}, room=user_sid)
    socketio.emit('livechat_request', {'sid': user_sid, 'message': original_message})

@socketio.on('admin_message')
def handle_admin_message(data):
    target_user_sid = data.get('sid')
    admin_msg = data.get('message')
    if target_user_sid in live_chat_queue:
        del live_chat_queue[target_user_sid]
    emit('live_reply', {'message': f"Admin: {admin_msg}"}, room=target_user_sid)
