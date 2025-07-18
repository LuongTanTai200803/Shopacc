from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from ..extensions import db, jwt
from ..models.acc import Acc
from ..models.user import User
from ..models.order import Order

import logging

logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG)

order_bp = Blueprint("order",__name__)

@order_bp.route("/payment", methods=["PATCH"])
@jwt_required()
def purchase():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        logger.debug(f"Data received for purchase: {data}")
        acc_id = data.get("id")
        price = int(data.get("price"))

        user = db.session.get(User, user_id)
        acc = db.session.get(Acc, acc_id)

        if not user or not acc:
            return jsonify({"error": "User or Acc not found"}), 404

        if user.coin - price <0:
            return jsonify({"msg": "Số coin không đủ"}), 400
        
        user.coin -= price

        order = Order(
            user_id=user_id,
            acc_id=acc_id,
            total_price=price,
            acc_name=acc.account_name,  
            acc_pass=acc.account_pass, 
            order_status='completed',
            purchase_date=db.func.current_timestamp()
        )
        db.session.add(order)
        db.session.commit()
        db.session.delete(acc)
        db.session.commit()

        return jsonify({"msg": "Mua tài khoản thành công",}), 200
    except Exception as e:
        logger.error(f"Error during purchase: {e}")
        return jsonify({"error": "Lỗi server"}), 500
    
@order_bp.route("/purchased-accounts", methods=["GET"])
@jwt_required()
def get_orders():
    try:
        user_id = get_jwt_identity()
        # Lấy tất cả các order của user, và TẢI LUÔN thông tin Acc liên quan
        orders = Order.query.filter_by(user_id=user_id).all()

        if not orders:
            return jsonify({"msg": "Bạn chưa có tài khoản nào được mua."}), 200 # Trả về 200 với thông báo, không phải 404

        order_list = []
        for order in orders:
            # Lấy thông tin Acc từ mối quan hệ
            # acc = order.acc # SQLAlchemy tự động tải acc do lazy=True

            # acc_data = {}
            # if acc: # Đảm bảo acc không phải là None nếu có lỗi dữ liệu
            #     acc_data = {
            #         "acc_id": acc.id,
            #         "acc_username": order.account_name,      # Thay bằng tên trường username trong model Acc
            #         "acc_password": order.account_pass,      # Thay bằng tên trường password trong model Acc
            #         "acc_status": acc.status,          # Thay bằng tên trường status trong model Acc
            #         "acc_description": acc.description # Thêm các trường khác của Acc nếu cần
            #     }

            order_data = {
                "order_id": order.id,
                "total_price": order.total_price,
                "order_status": "Đã bán",
                "acc_name": order.acc_name,
                "acc_pass": order.acc_pass,
                "purchase_date": order.purchase_date.isoformat() if order.purchase_date else None
                
            }
            order_list.append(order_data)

        return jsonify(order_list), 200
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({"error": "Lỗi server"}), 500