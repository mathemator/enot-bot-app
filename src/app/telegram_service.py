import logging

from app_config import API_HASH, API_ID, BOT_TOKEN
from telethon import TelegramClient


class TelegramService:
    def __init__(self):
        logging.info("initializing TelegramService")
        self.api_id = API_ID
        self.api_hash = API_HASH
        self.bot_token = BOT_TOKEN
        logging.info("TelegramService initizlized")

    async def get_group_users(self, group_id):
        logging.info(f"request on users for {group_id}")
        try:
            async with await TelegramClient("bot", self.api_id, self.api_hash).start(
                bot_token=self.bot_token
            ) as bot:
                chat = await bot.get_entity(int(group_id))
                participants = await bot.get_participants(chat)
                logging.info(f"participants of {group_id} successfully retrieved")
                return participants
        except Exception as e:
            logging.error(f"Error while retrieving chat data {e}")
            raise e
