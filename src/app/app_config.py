import os

from common.config import load_config

required_params = ["API_ID", "API_HASH", "BOT_TOKEN"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "app-config.json")

config_dict = load_config(CONFIG_FILE, required_params)
PORT = config_dict["PORT"]
API_ID = config_dict["API_ID"]
API_HASH = config_dict["API_HASH"]
BOT_TOKEN = config_dict["BOT_TOKEN"]
