# scripts/setup_logging.py
from app import setup_logging

import logging
logger = logging.getLogger(__name__) 


def main():
    setup_logging()
    print("✅ Logging configured.")

if __name__ == "__main__":
    main()
