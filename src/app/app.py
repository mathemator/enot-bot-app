import logging
from logging_config import setup_logging

setup_logging()

from app_config import config_dict

from flask import Flask
import routes


app = Flask(__name__)
app.register_blueprint(routes.blueprint)

if __name__ == '__main__':
    logging.info("Starting application")
    app.run(debug=False, port=config_dict['port'])
