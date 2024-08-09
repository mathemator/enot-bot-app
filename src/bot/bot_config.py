from common.config import load_config

required_params = ['api_id', 'api_hash', 'bot_token']

config_dict = load_config('bot-config.json', required_params)
api_id = config_dict['api_id']
api_hash = config_dict['api_hash']
bot_token = config_dict['bot_token']