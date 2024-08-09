import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                os.path.join(BASE_DIR, 'app.log'),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,  # Keep up to 5 backup logs
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )