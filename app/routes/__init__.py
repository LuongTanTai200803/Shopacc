from flask import jsonify
from app.models.user import User

def check_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user:
        return user
    else:
        return False
