from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(36), unique=True, nullable=True)     # Cho phép null nếu Google login
    email= db.Column(db.String(128), unique=True, nullable= True)      # Email sẽ là duy nhất
    password_hash = db.Column(db.String(256), nullable=True)            # Cho phép null nếu Google login
    google_id = db.Column(db.String(128), unique=True, nullable=True)   # ID từ Firebase/Google
   
    coin = db.Column(db.Integer, nullable=True, default=0)
    role = db.Column(db.String(10), default="User")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
