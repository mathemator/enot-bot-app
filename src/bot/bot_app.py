import logging
import threading
import time

import requests
import telebot

from bot_config import APP_PORT, BOT_TOKEN, DEVELOPER_ID
from logging_config import setup_logging
from participant_service import handle_all_command
from schedule_service import (
    get_all_schedules_service,
    create_schedule, schedule_checker,
    validate_schedule_command, cancel_schedule_service
)
from team_service import (
    handle_invite_team_participants,
    handle_team_delete,
    handle_team_kick,
    handle_team_mention,
    handle_team_set,
    handle_teams,
)

setup_logging()

bot = telebot.TeleBot(BOT_TOKEN)

current_chat_id = None


# Пример общего обработчика ошибок
def handle_error(error):
    logging.error(f"Error occurred: {error}")
    # Отправляем сообщение администратору или в группу
    # Если ошибка произошла в обработчике сообщения, можно получить chat_id из глобальных переменных или других механизмов
    if current_chat_id:
        try:
            bot.send_message(
                DEVELOPER_ID,
                text=f"Непредвиденная ошибка: {error}",
            )
        except Exception as e:
            logging.error(f"Error while sending error message {e}")


# ================== ТЕХНИЧЕСКИЕ ===================
@bot.message_handler(content_types=["new_chat_members", "left_chat_member"])
def on_new_chat_member(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        if message.content_type == "new_chat_members" and any(
                member.is_bot for member in message.new_chat_members
        ):
            handle_update(message, silent=True)
        else:
            handle_update(message, silent=False)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["update"])
def refresh_participants(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_update(message, silent=False)
    except Exception as e:
        handle_error(e)


# Обработчик команды /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(
        message,
        """
Привет! Я Енот Шустрик! 
Я помогаю вам созывать коллег для общения на важные темы. 
Набери /help, и увидишь, что я умею!
                """,
    )


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(
        message,
        """
Привет! Меня зовут Шустрик, я енот-программист. Вот что я умею:
/start  -   моё приветствие
/help   -   что я умею
/all <текст>   -    упомяну всех коллег для данного текста.\n\
Также доступна запись @all <текст>, если сообщение так начинается
/update вызываю мою систему для обновления списка коллег для чата
/teams  -   список всех команд группы
/team_set <имя команды> <список упоминаний участников> - установить команду. 
Обратите внимание, что работать будут именно упоминания
@team1 ... @teamN <текст> -   упомяну коллег из перечисленных команд данным текстом.\n\
обращаю внимание — только если сообщение с этого начинается и команды разделены пробелом
/team_delete <имя команды> - удаляю команду как отдельный список
/team_invite <имя команды> <упоминание1> .... <упоминаниеN> - добавить участников в команду
/team_kick <имя команды> <упоминание1> .... <упоминаниеN> - убрать участников из команды
/schedule -u @userN,@teamM,<mentionK> -d <Day1,DayN> -t 14:00 -m "Сообщение" -e дд-мм-ггг - где -u это список юзеров, команд, и упоминаний, -d дни недели на англ. типа Mon,Tue,Sun, -m сообщение, -e опциональное дата завершения
/schedules выводит список запланированных сообщений
/schedule_cancel <id> удаляет запланированное задание
                """,
    )


# ================== СООБЩЕНИЯ ===================
@bot.message_handler(
    func=lambda message: (not (message.text and message.text.startswith("/"))) and (
            (message.text and "@" in message.text)
            or (message.caption and "@" in message.caption)),
    content_types=["photo", "text", "video", "document"],
)
def handle_mention(message):
    global current_chat_id
    current_chat_id = message.chat.id
    message_text = message.text if message.text else message.caption
    try:
        if "@all" in message_text:
            handle_all_command(message, bot)
        else:
            handle_team_mention(message, bot)
    except Exception as e:
        handle_error(e)


# ================== КОМАНДЫ КОМАНД ===================
@bot.message_handler(commands=["all"])
def all(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_all_command(message, bot)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["team_invite"])
def team_set(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_invite_team_participants(message, bot)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["team_kick"])
def team_set(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team_kick(message, bot)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["team_set"])
def team_set(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_team_set(message, bot)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["teams"])
def teams(message):
    global current_chat_id
    current_chat_id = message.chat.id
    try:
        handle_teams(message, bot)
    except Exception as e:
        handle_error(e)


@bot.message_handler(commands=["team_delete"])
def team_delete(message):
    global current_chat_id

    current_chat_id = message.chat.id
    try:
        handle_team_delete(message, bot)
    except Exception as e:
        handle_error(e)


# TODO ПЕРЕНЕСТИ В АПДЕЙТ-СЕРВИС
def handle_update(message, silent):
    chat_id = message.chat.id
    response = requests.post(
        f"http://localhost:{APP_PORT}/update_participants/{chat_id}"
    )
    logging.info(f"response for {chat_id}: {response.text}")
    if silent:
        return
    if response.status_code == 200:
        bot.reply_to(message, "Обновил на своём компютере список коллег в чате!")
    else:
        bot.reply_to(
            message,
            "Упс, что-то пошло не так на моём компьютере. Не получилось обновить список коллег.",
        )


# ================== КОМАНДЫ ЗАДАЧ ===================
@bot.message_handler(commands=["schedule"])
def handle_schedule(message):
    args = message.text.split()  # Разделяем текст команды на части
    valid, result = validate_schedule_command(args)

    if not valid:
        bot.send_message(message.chat.id, result)
        return
    try:
        create_schedule(args, message)
        bot.send_message(message.chat.id, "Задача успешно запланирована!")
    # Далее можно вызвать schedule_service для сохранения задачи
    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=f"Ошибка создания задачи: {e}")


@bot.message_handler(commands=["schedule_cancel"])
def cancel_schedule(message):
    try:
        # Извлекаем ID задачи из сообщения
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Пожалуйста, укажите ID задачи для отмены.")
            return

        task_id = int(args[1])  # Предполагаем, что ID задачи передаётся вторым аргументом

        # Вызываем метод удаления задачи из repository
        result = cancel_schedule_service(task_id)

        if result:
            bot.reply_to(message, f"Задача с ID {task_id} успешно отменена.")
        else:
            bot.reply_to(message, f"Задача с ID {task_id} не найдена.")
    except ValueError:
        bot.reply_to(message, "Некорректный формат ID задачи.")
    except Exception as e:
        bot.reply_to(message, f"Ошибка при отмене задачи: {e}")


@bot.message_handler(commands=["schedules"])
def handle_schedules(message):
    try:
        schedules = get_all_schedules_service(message.chat.id)
        if schedules:
            bot.send_message(chat_id=message.chat.id, text="\n".join(schedules))
        else:
            bot.send_message(chat_id=message.chat.id, text="Нет активных задач.")
    except Exception as e:
        bot.send_message(chat_id=message.chat.id, text=f"Ошибка получения задач: {e}")


# ================== MAIN ===================
if __name__ == "__main__":
    logging.info("Starting bot")
    threading.Thread(target=schedule_checker, args=(bot,)).start()
    while True:
        try:
            bot.polling(timeout=60)
        except Exception as e:
            logging.error(f"Polling error: {e}")
            time.sleep(15)  # Задержка перед повторным запуском polling
