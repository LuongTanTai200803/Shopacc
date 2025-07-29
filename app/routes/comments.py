from flask import Blueprint, jsonify


comments_bp = Blueprint('comments', __name__)

from ..models.comment import Comment
from ..models.user import User
from ..extensions import db, cache

@comments_bp.route('', methods=['GET', 'POST'])
def get_comments():
    comments = Comment.query.all()
    comments_data = [{
        'id': comment.id,
        'user_id': comment.user_id,
        'content': comment.content,
        'created_at': comment.created_at.isoformat(),
        'user': {
            'id': comment.user.id,
            'username': comment.user.username
        }
    } for comment in comments]

    return jsonify(comments_data), 200