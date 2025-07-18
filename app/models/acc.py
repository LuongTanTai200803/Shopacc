from ..extensions import db

class Acc(db.Model):
    __tablename__ = "accs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    hero = db.Column(db.Integer, nullable=False)
    skin = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    rank = db.Column(db.Text, nullable=True, default="Unrank")
    image_url = db.Column(db.String(300), nullable=True)

    account_name = db.Column(db.String(100),unique=True, nullable=True)
    account_pass = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='available')  # available, sold, pending