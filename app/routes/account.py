from functools import wraps
import logging
from urllib.parse import urlencode

from sqlalchemy import func
from ..extensions import db, cache
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request

from ..models.user import User
from ..models.acc import Acc

import logging

logger = logging.getLogger(__name__) 

acc_bp = Blueprint("acc",__name__)

# logger = logging.getLogger(__name__)

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
    
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()  # xác thực token trước
        claims = get_jwt()

        role = claims.get("role")     # nếu bạn lưu "role" trong token

        if role != "Admin":
            return jsonify({"msg": "Admin access required"}), 403

        return fn(*args, **kwargs)
    return wrapper


def check_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user:
        return user
    else:
        return False

@acc_bp.route('/', methods=['GET'])
def get_acc():
    # Lấy toàn bộ query parameters
    query_params = request.args.to_dict()
    cache_key = f"accounts_view_cache:{urlencode(query_params)}" if query_params else "accounts_view_cache"

    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached), 200
    
    # Nếu có tham số tìm kiếm, lọc theo hero, skin hoặc description
    hero = request.args.get("hero")
    skin = request.args.get("skin")
    desc = request.args.get("desc")

    price_min = request.args.get("price_min", type=int)
    price_max = request.args.get("price_max", type=int)

    query = Acc.query
    logger.debug(f"request args: {request.args}")
    logger.debug(f"Filtering by hero: {hero}")

    
    if desc:
        query = query.filter(func.lower(Acc.description).contains(desc.lower()))
    if hero:
        query = query.filter(Acc.hero == int(hero))
    if skin:
        query = query.filter(Acc.skin == int(skin))
    if price_min is not None:
        query = query.filter(Acc.price >= price_min)
    if price_max is not None:
        query = query.filter(Acc.price <= price_max)

    # Nếu không có tham số tìm kiếm, lấy tất cả
    accs = query.all()

    acc_data = [
        {
            "id": acc.id,
            "hero": acc.hero,
            "skin": acc.skin,
            "price": acc.price,
            "description": acc.description,
            "image_url": acc.image_url
        }
        for acc in accs
    ]

    cache.set(cache_key, acc_data, timeout=60)
    return jsonify(acc_data), 200


@acc_bp.route('/<int:acc_id>', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)
def details_acc(acc_id):
    acc = Acc.query.filter_by(id=acc_id).first()

    if not acc:
        return jsonify({"error": "Account not found"}), 404
    
    acc_data = {
            "id": acc.id,
            "hero": acc.hero,
            "skin": acc.skin,
            "price": acc.price,
            "description": acc.description,
            "rank": acc.rank,
            "image_url": acc.image_url
        }

    return jsonify(acc_data), 200

@acc_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
def create_acc():
    data = request.get_json()

    if not all(field in data for field in ['hero', 'skin','price','description']):
        return jsonify({"msg": "Not Enough Data"}), 400
    
    acc = Acc (
            hero = data['hero'],
            skin = data['skin'],
            price = data['price'],
            description = data['description'] ,
            image_url = data['image_url']  
    )

    db.session.add(acc)
    db.session.commit()

    return jsonify({
        "msg": "Account created",
        "acc_id": acc.id 
                    }), 201


@acc_bp.route('/<int:acc_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_acc(acc_id):
    data = request.get_json()
    user_id = get_jwt_identity()
    acc = Acc.query.filter_by(id=acc_id).first()

    if not acc:
        return jsonify({"error": "Account not found"}), 404
    
    string_fields = ['hero', 'skin', 'price']
    for field in string_fields:
        value = data.get(field)
        if value not in (None, ""):
            setattr(acc, field, value)


    acc.description = data.get('description', acc.description)
    acc.rank = data.get('rank', acc.rank)
    acc.image_url = data.get('image_url', acc.image_url)

    db.session.commit()
    return jsonify({"msg": "Acc update success"}), 200


@acc_bp.route('/<int:acc_id>', methods=['DELETE'])
@jwt_required()
def del_acc(acc_id):
    acc = Acc.query.filter_by(id=acc_id).first()

    if not acc:
        return jsonify({"error": "Account not found"}), 404
    
    db.session.delete(acc)
    db.session.commit()
    return jsonify({"msg": "Mua acc thành công"}), 200


@acc_bp.route('/check')
@jwt_required()
@admin_required
def check_role():
    
    return jsonify({"msg": "Admin access! "}), 200
