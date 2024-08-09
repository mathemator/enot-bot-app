import logging

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bot_config import config_dict
from common.participant_service import get_participants_by_group

from logging_config import setup_logging

setup_logging()

bot_token = config_dict['bot_token']

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['update'])
def refresh_participants(message):
    chat_id = message.chat.id
    response = requests.post(f'http://localhost:5000/update_participants/{chat_id}')
    logging.info(f'response for {chat_id}: {response.text}')
    if response.status_code == 200:
        bot.reply_to(message, 'Обновил на своём компютере список коллег в чате!')
    else:
        bot.reply_to(message, 'Упс, что-то пошло не так на моём компьютере. Не получилось обновить список коллег.')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
                 """
Привет! Я Енот Шустрик! 
Я помогаю вам созывать коллег для общения на важные темы. 
Набери /help, и увидишь, что я умею!
                """)
    
@bot.message_handler(commands=['help'])
def help(message):
    bot.reply_to(message, 
                 """
/start  -   моё приветствие
/help   -   что я умею
/all    -   отвечу на твоё сообщение, позвав при этом всех коллег в чате
/refresh    -   вызываю мою систему для обновления списка коллег для чата
                """)

@bot.message_handler(commands=['all'])
def send_all_users(message):
    group_id = message.chat.id

    # Проверка прав бота
    bot_member = bot.get_chat_member(group_id, bot.get_me().id)
    if not (bot_member.can_delete_messages):
        # Отправка сообщения с инструкциями
        bot.send_message(chat_id=group_id, text="У меня нет нужных прав для выполнения этой команды. "
                                                "Пожалуйста, предоставьте права администратора на удаление сообщений.")
        return

    participants = get_participants_by_group(group_id)

    if not participants:
        bot.send_message(
            chat_id=message.chat.id,
            text='Ой, похоже, у меня ещё нет данных об участниках. Попробуйте команду на обновление.',
            message_thread_id=message.message_thread_id if message.is_topic_message else None
        )

    # Получение ID бота
    bot_id = bot.get_me().id

    # Создание строки с упоминаниями
    mentions = ', '.join(
        f"[{participant.first_name or ''} {participant.last_name or ''}](tg://user?id={participant.id})"
        for participant in participants
        if participant.id != bot_id
    )

    # Получение текста сообщения без команды
    message_text = message.text.split(maxsplit=1)
    if len(message_text) > 1:
        message_text = message_text[1]
    else:
        message_text = ""

    # Создание нового текста сообщения
    author_name = f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()

    # Создание нового текста сообщения
    full_message = f"{author_name} написал:\n{message_text}\n{mentions}"

    # Отправка нового сообщения с разметкой MarkdownV2
    bot.send_message(
        chat_id=message.chat.id,
        text=full_message,
        parse_mode='MarkdownV2',
        message_thread_id=message.message_thread_id if message.is_topic_message else None
    )

    # Удаление только исходного сообщения
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

if __name__ == '__main__':
    logging.info('Starting bot')
    bot.polling()