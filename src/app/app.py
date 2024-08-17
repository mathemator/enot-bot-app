import logging

from logging_config import setup_logging

setup_logging()

import routes
from app_config import PORT
from flask import Flask

app = Flask(__name__)
app.register_blueprint(routes.blueprint)

if __name__ == "__main__":
    logging.info("Starting application")
    app.run(debug=False, port=PORT)
