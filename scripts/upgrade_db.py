# scripts/upgrade_db.py
from alembic.command import upgrade
from alembic.config import Config as AlembicConfig
from app import create_app

def main():
    app = create_app()
    with app.app_context():
        alembic_cfg = AlembicConfig("migrations/alembic.ini")
        try:
            upgrade(alembic_cfg, "head")
            print("✅ Alembic upgrade successful.")
        except Exception as e:
            print(f"❌ Alembic upgrade failed: {e}")
            raise

if __name__ == "__main__":
    main()
