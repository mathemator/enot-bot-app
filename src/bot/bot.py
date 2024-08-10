import logging

import telebot
import requests

from participant_service import handle_all_command
from team_service import handle_team, handle_teams, handle_team_delete, handle_team_set, handle_team_mention
from bot_config import config_dict

from logging_config import setup_logging

setup_logging()

bot_token = config_dict['bot_token']

bot = telebot.TeleBot(bot_token)

current_chat_id = None

# Пример общего обработчика ошибок
def handle_error(error):
    logging.error(f"Error occurred: {error}")
    # Отправляем сообщение администратору или в группу
    # Если ошибка произошла в обработчике сообщения, можно получить chat_id из глобальных переменных или других механизмов
    if current_chat_id:
        bot.send_message(current_chat_id, text=f"Непредвиденная ошибка: {error}, обратитесь к @mathemator")

@bot.message_handler(commands=['update'])
def refresh_participants(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        chat_id = message.chat.id
        response = requests.post(f'http://localhost:5000/update_participants/{chat_id}')
        logging.info(f'response for {chat_id}: {response.text}')
        if response.status_code == 200:
            bot.reply_to(message, 'Обновил на своём компютере список коллег в чате!')
        else:
            bot.reply_to(message, 'Упс, что-то пошло не так на моём компьютере. Не получилось обновить список коллег.')
    except Exception as e:
        handle_error(e)


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
/all <текст>   -   упомяну всех коллег для данного текста
/update вызываю мою систему для обновления списка коллег для чата
/team_set <имя команды> <список упоминаний участников> - установить команду. 
Обратите внимание, что работать будут именно упоминания
/team <имя команды> <текст> -   упомяну коллег из данной команды с данным текстом.\n\
также есть короткая запись: @<имя команды>, но — обращаю внимание — только если сообщение с этого начинается
/teams  -   список всех команд
/team_delete <имя команды> - удаляю команду как отдельный список
                """)

@bot.message_handler(commands=['all'])
def all(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_all_command(message, bot)
    except Exception as e:
        handle_error(e)

@bot.message_handler(commands=['team_set'])
def team_set(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team_set(message, bot)
    except Exception as e:
        handle_error(e)

@bot.message_handler(func=lambda message: message.text.startswith('@'))
def handle_mention(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team_mention(message, bot)
    except Exception as e:
        handle_error(e)

@bot.message_handler(commands=['team'])
def team(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team(message, bot)
    except Exception as e:
        handle_error(e)

@bot.message_handler(commands=['teams'])
def teams(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_teams(message, bot)
    except Exception as e:
        handle_error(e)

@bot.message_handler(commands=['team_delete'])
def team_delete(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team_delete(message, bot)
    except Exception as e:
        handle_error(e)

if __name__ == '__main__':
    logging.info('Starting bot')
    bot.polling()