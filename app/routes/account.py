from functools import wraps
from app.extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request

from app.models.user import User
from app.models.acc import Acc


acc_bp = Blueprint("acc",__name__)

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
@jwt_required()
def get_acc():

    accs = Acc.query.filter_by().all()

    acc_data = [
        {
            "id": acc.id,
            "hero": acc.hero,
            "skin": acc.skin,
            "price": acc.price,
            "description": acc.description,
            "image": acc.image_url
        }
        for acc in accs
    ]

    return jsonify(acc_data), 200

@acc_bp.route('/<int:acc_id>', methods=['GET'])
@jwt_required()
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
            "image": acc.image_url
        }

    return jsonify(acc_data), 200

@acc_bp.route('/', methods=['POST'])
@jwt_required()
@admin_required
@admin_required
def create_acc():
    data = request.get_json()

    if not all(field in data for field in ['hero', 'skin','price','description']):
        return jsonify({"msg": "Not Enough Data"}), 400
    
    acc = Acc (
            hero = data['hero'],
            skin = data['skin'],
            price = data['price'],
            description = data['description']   
    )
    db.session.add(acc)
    db.session.commit()

    return jsonify({
        "msg": "Account created",
        "acc_id": acc.id 
                    }), 201

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
