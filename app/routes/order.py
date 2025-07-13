from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from ..extensions import db, jwt
from ..models.acc import Acc
from ..models.user import User

import logging

logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    # Gắn handler từ root để logger này không bị “mute”
    logger.propagate = True
order_bp = Blueprint("order",__name__)

@order_bp.route("/payment", methods=["PATCH"])
@jwt_required()
def purchase():
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
    db.session.delete(acc)
    db.session.commit()

    return jsonify({"msg": "Mua tài khoản thành công"}), 200
