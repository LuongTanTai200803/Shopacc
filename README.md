# ShopAcc
API cho hệ thống bán tài khoản game
## Tính năng

- [x] Đăng ký, đăng nhập người dùng
- [x] CRUD tài khoản game (chỉ dành cho admin)
- [ ] Tìm kiếm tài khoản
- [x] Mua/bán tài khoản (thanh toán ảo)
- [x] Phân quyền người dùng theo token (admin/user)

### Tech stack:
Python (Flask), REST API, SQLAlchemy + MySQL/PostgreSQL, Redis, Deploy: Railway -> (Nginx) + Gunicorn, JWT.

## ⚙️ Cài đặt (Local)

```bash
# 1. Clone project
git clone https://github.com/LuongTanTai200803/Shopacc.git
cd Shopacc/backend/

# 2. Tạo môi trường ảo & cài package
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Tạo file .env từ mẫu
cp .env.example .env

# 4. Chạy local
python run.py
