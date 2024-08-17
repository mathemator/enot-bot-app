import os

from common.config import load_config

required_params = ["BOT_TOKEN"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "bot-config.json")

config_dict = load_config(CONFIG_FILE, required_params)
BOT_TOKEN = config_dict["BOT_TOKEN"]
APP_PORT = config_dict["APP_PORT"]

