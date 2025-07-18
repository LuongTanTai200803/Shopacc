from ..extensions import db

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    acc_id = db.Column(db.Integer, db.ForeignKey('accs.id', ondelete='SET NULL'), nullable=True)
    total_price = db.Column(db.Integer, nullable=False)
    order_status = db.Column(db.String(20), default='pending')  # pending, completed
     
    purchase_date = db.Column(db.DateTime, nullable=True)
    acc_name = db.Column(db.String(100), nullable=True)
    acc_pass = db.Column(db.String(100), nullable=True)
