from common.config import load_config
import os

required_params = ['api_id', 'api_hash', 'bot_token']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, 'app-config.json')

config_dict = load_config(CONFIG_FILE, required_params)
api_id = config_dict['api_id']
api_hash = config_dict['api_hash']
bot_token = config_dict['bot_token']