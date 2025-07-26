from functools import wraps
import os

import firebase_admin
from flask import Blueprint, json, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from ..extensions import db, jwt, cache
from ..models.user import User


auth_bp = Blueprint("auth",__name__)

import logging

logger = logging.getLogger(__name__) 


def rate_limit_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.path == '/auth/login':
            ip = request.remote_addr
            key = f"login_rate_limit:{ip}"
            attempts = cache.get(key) or 0
            print(f"Login attempts for {ip}: {attempts}")
            if attempts >= 5:
                return jsonify({"msg": "Too many login attempts. Please try again later."}), 429
            
            cache.set(key, attempts + 1, timeout=60)  # Reset after 60 seconds
            return fn(*args, **kwargs)
    
    return wrapper

@auth_bp.route('/ping')
def ping():
    return "pong", 200


@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        
        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "User exists"}), 409

        # Kiểm tra field cần thiết
        if not all(field in data for field in ['username', 'password']):
            return jsonify({"msg": "Not Enough Data"}), 400
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({"msg": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"message": "Lỗi server", "error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
@rate_limit_login
def login():
    
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Kiểm tra field cần thiết
    if not all(field in data for field in ['username', 'password']):
        return jsonify({"msg": "Not Enough Data"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password) :
        return jsonify({"msg": "Sai tên hoặc mật khẩu"}), 401
    
    # Kiểm tra token trong Redis
    cached_token = cache.get(f"user_token:{user.id}")
    if cached_token:
        return jsonify({
            "msg": "Đăng nhập thành công (token cũ)",
            "username": user.username,
            "coin": user.coin,
            "access_token": cached_token
        }), 200

    # Nếu không có token cũ, tạo mới
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    cache.set(f"user_token:{user.id}", access_token, timeout=900)

    return jsonify({
        "msg": "Đăng nhập thành công",
        "coin": user.coin,
        "username": user.username,
        "access_token": access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    user_data = {
            "id": user.id,
            "username": user.username or user.email,
            "coin": user.coin
        }

    return jsonify(user_data), 200

@auth_bp.route('/', methods=['PUT'])
@jwt_required()
def put_coin():
    data = request.get_json()
    user_id = data.get("id_guest")
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"msg": "User not exist"}), 404
    
    coin = int(data['coin'])
    print(f"Received coin: {coin}")
    if   coin < 0 :
        return jsonify({"msg": "wrong value"}),400
    
    user.coin += data.get('coin', user.coin)

    db.session.commit()

    return jsonify({"msg": f"User {user_id} received {coin}"}), 200

@auth_bp.route('/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({"msg": "You are logged in!",
                    "user_id": user_id}), 200


from firebase_admin import credentials, auth

json_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")

creds_dict = json.loads(json_creds)

# Tạo credential từ dict
cred = credentials.Certificate(creds_dict)
firebase_admin.initialize_app(cred)

@auth_bp.route("/google", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("idToken")
    logger.info(f"[Google Login] id_token: {id_token}")

    try:
        decoded_token = auth.verify_id_token(id_token)
        google_id = decoded_token["uid"]
        email = decoded_token.get("email")

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(email=email, google_id=google_id)
            db.session.add(user)
            db.session.commit()

            # Kiểm tra token trong Redis
        cached_token = cache.get(f"user_token:{user.id}")
        if cached_token:
            return jsonify({
                "msg": "Đăng nhập thành công (token cũ)",
                "usernaem": user.email,
                "coin": user.coin,
                "access_token": cached_token
            }), 200

        # Nếu không có token cũ, tạo mới
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        cache.set(f"user_token:{user.id}", access_token, timeout=900)

        return jsonify({
            "coin": user.coin,
            "username": user.email,
            "access_token": access_token}),200

    except Exception as e:
        import traceback
        print("[Firebase Verify Error]", traceback.format_exc())
        return jsonify({"error": "Server error", "detail": str(e)}), 401
