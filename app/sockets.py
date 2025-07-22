import re
import random
import json
import os
import uuid 

from flask import request, url_for, current_app
from .extensions import socketio
from .models import Acc
from sqlalchemy import func
from flask_socketio import emit
import google.generativeai as genai
from gtts import gTTS
# --- PHẦN CẤU HÌNH VÀ TẢI DỮ LIỆU (Giữ nguyên) ---
live_chat_queue = {}
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)
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
def create_audio_response(text_to_speak):
    """
    Tạo file MP3 từ văn bản bằng gTTS, sau khi đã xử lý để đọc tự nhiên hơn.
    """
    try:
        # --- NÂNG CẤP TOÀN DIỆN LOGIC XỬ LÝ VĂN BẢN ---
        
        # 1. Tạo bản sao văn bản để xử lý riêng cho gTTS
        text_for_gtts = text_to_speak

        # 2. Xử lý các từ viết tắt và tên riêng
        # Dạy nó đọc "ShopACC" thành "Shop Ác" cho tự nhiên
        text_for_gtts = text_for_gtts.replace('ShopACC', 'Shop Ạc')
        text_for_gtts = text_for_gtts.replace('ACC', 'Ạc')
        
        # Dạy nó đọc "LMHT" thành "liên minh huyền thoại"
        text_for_gtts = text_for_gtts.replace('LMHT', 'liên minh huyền thoại')

        # 3. Loại bỏ các ký tự đặc biệt của Markdown
        # Dùng regex để xóa tất cả các ký tự '*' và '#'
        text_for_gtts = re.sub(r'[\*#"]', '', text_for_gtts)

        # 4. Xử lý các trường hợp khác để âm thanh mượt hơn
        # Thay thế dấu xuống dòng bằng dấu phẩy để có nhịp nghỉ
        text_for_gtts = text_for_gtts.replace('\n', ', ')

        # ---------------------------------------------------

        # Tạo tên file ngẫu nhiên
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_FOLDER, filename)

        # Tạo âm thanh với văn bản đã được "huấn luyện"
        tts = gTTS(text=text_for_gtts, lang='vi', slow=False)
        tts.save(filepath)
        
        # Trả về URL
        with current_app.app_context():
            audio_url = url_for('static', filename=f'audio/{filename}', _external=True)
        return audio_url

    except Exception as e:
        print(f"Lỗi khi tạo file audio: {e}")
        return None
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
        # BẢN MÔ TẢ CÔNG VIỆC CỦA TRỢ LÝ ẢO TẠI SHOPACC #

        ## 1. BẠN LÀ AI?
        - **Tên:** Bot.
        - **Vai trò:** Chuyên gia tư vấn tài khoản game tại ShopACC.
        - **Tính cách:** Hãy trò chuyện như một người bạn am hiểu về game, **nhiệt tình, thân thiện và đáng tin cậy**. Giọng văn tự nhiên, không quá máy móc.

        ## 2. MỤC TIÊU CHÍNH
        - Giúp khách hàng tìm được tài khoản **Liên Minh Huyền Thoại** ưng ý nhất dựa trên nhu cầu và ngân sách của họ.
        - Mang lại trải nghiệm tư vấn chuyên nghiệp và vui vẻ.

        ## 3. QUY TRÌNH TƯ VẤN
        - **Khi khách hỏi chung chung (ví dụ: "tìm acc đi shop"):** Nếu không có DỮ LIỆU THAM KHẢO, hãy **chủ động hỏi lại** để làm rõ nhu cầu của khách: "Chào bạn, để mình tìm acc chuẩn nhất cho bạn, bạn cho mình biết thêm về rank, tướng yêu thích, hoặc tầm giá bạn quan tâm được không?"
        - **Khi có DỮ LIỆU THAM KHẢO:** Đây là danh sách các tài khoản có sẵn trong shop. Nhiệm vụ của bạn là:
            - Trình bày các lựa chọn một cách **rõ ràng, súc tích**.
            - **Nêu bật các điểm đặc biệt** của từng tài khoản (ví dụ: "Acc ID 123 có skin Yasuo Ma Kiếm đó bạn ơi!").
            - Dựa vào câu hỏi của khách để đưa ra gợi ý phù hợp nhất từ danh sách này.
        - **Định dạng câu trả lời:** Luôn sử dụng **Markdown** để câu trả lời dễ đọc.
            - Dùng **gạch đầu dòng (`-`)** để liệt kê tài khoản.
            - Dùng **in đậm (`**...**`)** để nhấn mạnh các thông tin quan trọng như tên skin hiếm, rank cao, hoặc giá tốt.

        ## 4. CÁC QUY TẮC BẤT DI BẤT DỊCH
        - **TRUNG THỰC:** **Tuyệt đối không bịa đặt thông tin** tài khoản không có trong DỮ LIỆU THAM KHẢO. Nếu không tìm thấy tài khoản phù hợp, hãy nói thật: "Tiếc quá, hiện tại shop mình chưa có acc nào khớp với yêu cầu của bạn. Bạn xem thử các acc này nhé, cũng khá ổn đó!"
        - **TẬP TRUNG:** Chỉ thảo luận về game **Liên Minh Huyền Thoại** và các tài khoản do ShopACC bán. Lịch sự từ chối các chủ đề không liên quan (ví dụ: "Shop có bán acc Valorant không?" -> "Dạ hiện tại shop mình chỉ chuyên về Liên Minh Huyền Thoại thôi ạ.").
        - **AN TOÀN:** Không trả lời các câu hỏi về hack/cheat, cày thuê, hoặc các hoạt động vi phạm điều khoản của game.
        - **BẢO MẬT:** Không hỏi hay yêu cầu khách hàng cung cấp thông tin cá nhân nhạy cảm.
        """
        if context:
            system_prompt += f"\n\nDỮ LIỆU THAM KHẢO:\n{context}"
        content_to_send = f"{system_prompt}\n\nCâu hỏi của khách hàng: '{user_message}'"

    elif task == 'rephrase':
        system_prompt = """
        # CHUYÊN GIA DIỄN ĐẠT LẠI CÂU VĂN #

        ## 1. VAI TRÒ CỦA BẠN
        - Bạn là một chuyên gia giao tiếp của ShopACC, chuyên biến những câu trả lời có sẵn (hơi khô khan) thành những đoạn hội thoại tự nhiên, thu hút và thân thiện.
        - **Tông giọng:** Hãy nói chuyện như một người bạn game thủ, nhiệt tình, nhưng vẫn chuyên nghiệp và đáng tin cậy.

        ## 2. NHIỆM VỤ
        - Nhận một "Câu gốc" và diễn đạt lại nó.
        - **Mục tiêu:** Làm cho câu trả lời của bot bớt "robot" và giống người hơn, tạo cảm giác gần gũi cho khách hàng.

        ## 3. VÍ DỤ ĐỂ BẠN HỌC THEO
        - **Ví dụ 1:**
            - **Câu gốc:** "Để thanh toán, bạn có thể chuyển khoản qua ngân hàng."
            - **Diễn đạt lại:** "Chắc chắn rồi ạ! Về thanh toán, bạn có thể chuyển khoản qua ngân hàng một cách nhanh chóng và tiện lợi nhé."
        - **Ví dụ 2:**
            - **Câu gốc:** "Chào bạn."
            - **Diễn đạt lại:** "ShopACC xin chào! Mình có thể hỗ trợ gì cho bạn hôm nay không ạ?"
        - **Ví dụ 3:**
            - **Câu gốc:** "Cảm ơn bạn đã mua hàng."
            - **Diễn đạt lại:** "Cảm ơn bạn đã tin tưởng và ủng hộ ShopACC! Nếu cần hỗ trợ gì thêm, đừng ngần ngại nhắn cho mình nhé."

        ## 4. QUY TẮC BẮT BUỘC
        - **GIỮ NGUYÊN Ý CHÍNH:** Phải giữ lại 100% ý nghĩa và thông tin cốt lõi của câu gốc.
        - **KHÔNG THÊM THÔNG TIN MỚI:** Tuyệt đối không được thêm bất kỳ thông tin nào không có trong câu gốc.
        - **TỰ NHIÊN:** Tránh dùng từ ngữ quá trang trọng, sáo rỗng. Hãy dùng ngôn ngữ đời thường, gần gũi.
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
    if not numbers:
        # Nâng cấp: Nếu không có số, nhờ AI hỏi lại ID
        return ask_gemini_ai(task='answer', user_message=user_message, context="Khách hàng đang muốn xem chi tiết tài khoản nhưng chưa cung cấp ID. Hãy hỏi lại họ cần xem ID nào.")
    try:
        acc_id = int(numbers[0])
        account = Acc.query.get(acc_id)
        if account:
            return f"Bot: Thông tin tài khoản ID {acc_id}:\n- Tướng: {account.hero}\n- Skin: {account.skin}\n- Giá: {account.price:,.0f} VNĐ."
        return f"Bot: Rất tiếc, không tìm thấy tài khoản nào có ID là {acc_id}."
    except (ValueError, IndexError):
        return "Bot: ID tài khoản không hợp lệ."


def handle_consultation(user_message, numbers):
    price_limit = parse_price_from_message(user_message)
    if price_limit:
        accounts = Acc.query.filter(Acc.price <= price_limit).order_by(Acc.price.desc()).limit(5).all()
        if not accounts:
            return f"Bot: Rất tiếc, hiện tại shop không có tài khoản nào trong tầm giá {price_limit:,.0f} VNĐ."
        context_for_ai = f"Dưới đây là một vài tài khoản Liên Minh Huyền Thoại có giá dưới hoặc bằng {price_limit:,.0f} VNĐ. Hãy dựa vào đây để tư vấn cho khách hàng:\n"
    else:
        accounts = Acc.query.order_by(func.random()).limit(5).all()
        if not accounts:
            return "Bot: Rất tiếc, cửa hàng hiện tại chưa có tài khoản nào để tư vấn cho bạn."
        context_for_ai = "Khách hàng đang cần tư vấn một tài khoản Liên Minh Huyền Thoại nhưng chưa đưa ra mức giá. Dưới đây là một vài tài khoản ngẫu nhiên đang có ở shop, hãy dựa vào đây để gợi ý và hỏi thêm khách hàng về nhu cầu của họ (rank, tướng, skin...):\n"
    for acc in accounts:
        context_for_ai += f"- ID {acc.id}: Giá {acc.price:,.0f} VNĐ, có {acc.hero} tướng, {acc.skin} skin.\n"
    return ask_gemini_ai(task='answer', user_message=user_message, context=context_for_ai)
COMPLEX_HANDLERS = [
    {"keywords": ["chi tiết", "thông tin", "xem acc"], "handler": handle_account_details},
    {"keywords": ["tư vấn", "gợi ý", "nên mua"], "handler": handle_consultation},
]
# =================================================================
def emit_reply_with_audio(text_response, user_sid):
    """
    Hàm trung tâm: nhận văn bản, tạo audio, và gửi cả hai cho client.
    """
    # Tạo URL âm thanh từ văn bản phản hồi
    audio_url = create_audio_response(text_response)

    # Gửi sự kiện 'bot_reply' với cả message và audioUrl
    emit('bot_reply', {'message': text_response, 'audioUrl': audio_url}, room=user_sid)
def classify_intent(user_message):
    """
    Dùng AI để phân tích câu nói của người dùng và trả về ý định chính.
    """
    if not gemini_model:
        return 'other' # Fallback nếu AI lỗi

    prompt = f"""
    Bạn là một bộ não phân loại ý định cho chatbot của cửa hàng game ShopACC.
    Dựa vào câu nói của khách hàng, hãy phân loại nó vào MỘT trong các danh mục sau.
    Chỉ trả về TÊN DANH MỤC, không thêm bất kỳ giải thích nào.

    DANH MỤC:
    - 'ask_details': Khách hàng muốn xem thông tin chi tiết về một tài khoản cụ thể, thường nhắc đến "ID", "xem acc", "thông tin acc".
        Ví dụ: "xem acc id 123", "cho mình xin thông tin con acc 50", "acc 99 có gì?"
    - 'consult_account': Khách hàng muốn tư vấn, tìm kiếm, hoặc xem các tài khoản nói chung. Đây là ý định phổ biến nhất.
        Ví dụ: "tìm acc dưới 200k", "có acc nào ngon không shop", "shop có bán acc gì", "cho xem vài con acc xịn"
    - 'greeting_and_info': Khách hàng đang chào hỏi, cảm ơn, hoặc hỏi các thông tin chung có câu trả lời cố định (như cách thanh toán).
        Ví dụ: "xin chào", "cảm ơn shop", "shop thanh toán thế nào?"
    - 'other': Câu hỏi không liên quan đến việc mua bán tài khoản (ví dụ: "shop ở đâu", "game này chơi hay không?").

    Câu nói của khách hàng: "{user_message}"
    TÊN DANH MỤC:
    """
    try:
        response = gemini_model.generate_content(prompt)
        intent = response.text.strip().replace("'", "").replace('"', '')
        print(f"AI classified intent as: '{intent}'")
        # Đảm bảo AI trả về một trong các intent hợp lệ
        valid_intents = ['ask_details', 'consult_account', 'greeting_and_info', 'other']
        if intent in valid_intents:
            return intent
        return 'consult_account' # Mặc định là tư vấn nếu AI trả về linh tinh
    except Exception as e:
        print(f"Lỗi khi phân loại ý định: {e}")
        return 'consult_account' # Mặc định là tư vấn nếu có lỗi
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
    original_message = data.get('message', '')
    user_sid = request.sid
    numbers = re.findall(r'\d+', original_message)

    # Bước 1: Dùng "bộ não" AI để hiểu ý định của khách
    intent = classify_intent(original_message)

    # Bước 2: Dựa vào ý định đã phân loại để hành động
    if intent == 'greeting_and_info':
        # Tìm intent tương ứng trong file JSON để lấy câu trả lời mẫu
        matched_intent = next((i for i in JSON_INTENTS if any(keyword in original_message.lower() for keyword in i["keywords"])), None)
        # Nếu không khớp từ khóa nào, mặc định là chào hỏi
        if not matched_intent:
            matched_intent = next((i for i in JSON_INTENTS if i["tag"] == "greeting"), None)
        
        base_response = random.choice(matched_intent["responses"])
        final_response = ask_gemini_ai(task='rephrase', context=base_response) or base_response
        emit_reply_with_audio(final_response, user_sid)

    elif intent == 'ask_details':
        response = handle_account_details(original_message, numbers)
        emit_reply_with_audio(response, user_sid)

    elif intent == 'consult_account':
        response = handle_consultation(original_message, numbers)
        emit_reply_with_audio(response, user_sid)

    else: # 'other' hoặc các trường hợp AI không phân loại được
        ai_response = ask_gemini_ai(task='answer', user_message=original_message)
        if ai_response:
            emit_reply_with_audio(ai_response, user_sid)
        else:
            fallback_to_live_chat(user_sid, original_message)

def fallback_to_live_chat(user_sid, original_message):
    if user_sid not in live_chat_queue:
        live_chat_queue[user_sid] = original_message
        bot_response = "Bot: Tôi chưa hiểu rõ câu hỏi của bạn. Vui lòng chờ để được kết nối với nhân viên hỗ trợ."
    else:
        bot_response = "Bot: Nhân viên hỗ trợ sẽ trả lời bạn ngay. Vui lòng chờ một chút."
    
    emit_reply_with_audio(bot_response, user_sid) 
    socketio.emit('livechat_request', {'sid': user_sid, 'message': original_message})

@socketio.on('admin_message')
def handle_admin_message(data):
    target_user_sid = data.get('sid')
    admin_msg = data.get('message')
    if target_user_sid in live_chat_queue:
        del live_chat_queue[target_user_sid]
    emit('live_reply', {'message': f"Admin: {admin_msg}"}, room=target_user_sid)
