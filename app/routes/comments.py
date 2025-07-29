from flask import Blueprint, jsonify, request


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
        'rating': comment.rating,
        
    } for comment in comments]

    return jsonify(comments_data), 200

@comments_bp.route('/post', methods=['OPTION','POST'])
def post_comment():
    data = request.get_json()
    if not data or 'content' not in data or 'rating' not in data:
        return jsonify({"error": "Invalid input"}), 400

    new_comment = Comment(
        user_id=data.get('user_id', 1),  # Default to user_id 1 for demo
        content=data['content'],
        rating=data['rating']
    )
    
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment posted successfully", "comment_id": new_comment.id}), 201