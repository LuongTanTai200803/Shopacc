from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from routes import check_user
from app.extensions import db
from models.user import User, check_password
auth_bp = Blueprint("auth",__name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    # Kiểm tra field cần thiết
    if not all(field in data for field in ['username', 'password']):
        return jsonify({"msg": "Not Enough Data"}), 400
    
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password) :
        return jsonify({"msg": "Bad credentials"}), 401
    # Tạo token
    access_token = create_access_token(identity=user.id)

    return jsonify({
        "msg": "Đăng nhập thành công",
        "token": access_token}), 200

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

    user.coin = data.get('coin', user.coin)

    db.session.commit()
    return profile(), 200 