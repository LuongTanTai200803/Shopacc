# scripts/wait_for_db.py
from app import create_app, wait_for_db
from app.extensions import db

def main():
    app = create_app()
    wait_for_db(app, db)
    print("✅ Database is ready.")

if __name__ == "__main__":
    main()
