import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler(
                os.path.join(APP_DIR, "app.log"),
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5,  # Keep up to 5 backup logs
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
    )
