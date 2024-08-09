from app_config import config_dict
from telethon import TelegramClient
import logging


class TelegramService:
    def __init__(self):
        logging.info('initializing TelegramService')
        self.api_id = config_dict['api_id']
        self.api_hash = config_dict['api_hash']
        self.bot_token = config_dict['bot_token']
        logging.info('TelegramService initizlized')

    async def get_group_users(self, group_id):
        logging.info(f'request on users for {group_id}')
        try:
            async with await TelegramClient('bot', self.api_id, self.api_hash).start(bot_token=self.bot_token) as bot:
                chat = await bot.get_entity(int(group_id))
                participants = await bot.get_participants(chat)
                logging.info(f'participants of {group_id} successfully retrieved')
                return participants
        except Exception as e:
            logging.error(f'Error while retrieving chat data {e}')
            raise e
