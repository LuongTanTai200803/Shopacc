from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from app.extensions import db, jwt
from app.models.user import User


auth_bp = Blueprint("auth",__name__)

import logging

logger = logging.getLogger(__name__) 

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
def login():
    logger.error("Đã vào api")
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Kiểm tra field cần thiết
    if not all(field in data for field in ['username', 'password']):
        return jsonify({"msg": "Not Enough Data"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password) :
        return jsonify({"msg": "Sai tên hoặc mật khẩu"}), 401
    # Tạo token
    access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "msg": "Đăng nhập thành công",
        "access_token": access_token}), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()

    user_data = {
            "id": user.id,
            "username": user.username,
            "coin": user.coin
        }

    return jsonify(user_data), 200

@auth_bp.route('/', methods=['PUT'])
@jwt_required()
def put_coin():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.filter_by(id=user_id).first()
    coin = int(data['coin'])
    if   coin < 0 :
        return jsonify({"msg": "wrong value"}),400
    
    user.coin += int(data.get('coin', user.coin))

    db.session.commit()

    return jsonify({f"msg": "Coins received {data.get['coin']}"}), 200

@auth_bp.route('/protected')
@jwt_required()
def protected():
    user_id = get_jwt_identity()
    return jsonify({"msg": "You are logged in!",
                    "user_id": user_id}), 200





