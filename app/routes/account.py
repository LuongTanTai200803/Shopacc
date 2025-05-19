from app.extensions import db
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.models.user import User
from app.models.acc import Acc


acc_bp = Blueprint("acc",__name__)

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
