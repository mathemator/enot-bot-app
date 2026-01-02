import re
import time
from datetime import datetime
from datetime import timedelta, timezone

from common.repository import save_scheduled_task, delete_scheduled_task, \
    get_active_schedules_by_chat, get_active_schedules, get_participants_by_group
from team_service import get_complete_mentions
from utils import create_mentions_text
from calendar_service import is_workday

moscow_offset = timedelta(hours=3)
# Создаём объект timezone с нужным смещением
moscow_tz = timezone(moscow_offset)


def schedule_checker(bot):
    while True:
        check_and_send_tasks(bot)
        time.sleep(60)  # Ждем 1 минуту перед следующей проверкой


def check_and_send_tasks(bot):
    today = datetime.date.today()

    if not is_workday(today):
        return

    # Получаем активные задачи
    active_tasks = get_active_schedules_service()
    # todo проработать момент с таймзонами
    current_time = datetime.now(moscow_tz).strftime("%H:%M")
    current_day = datetime.now(moscow_tz).strftime("%a")

    for task in active_tasks:
        # Проверяем совпадение по времени и дню
        time_with_margin = (datetime.strptime(task.time, "%H:%M") - timedelta(minutes=1)).strftime("%H:%M")
        if current_time == time_with_margin and current_day in task.days:
            # Отправляем сообщение в чат
            mentioned_participants = []
            participants = get_participants_by_group(task.chat_id)
            # Формируем список участников для упоминания
            for p in participants:
                if str(p.id) in task.recipients.split(','):
                    mentioned_participants.append(p)

            bot.send_message(chat_id=task.chat_id,
                             text=create_mentions_text(participants=mentioned_participants,
                                                       init_text=task.message),
                             parse_mode="MarkdownV2",
                             message_thread_id=task.thread_id
                             )
            # Можно дополнительно обработать повторяемость или активность задачи


def validate_schedule_command(args):
    errors = []

    # Проверка получателей (-u)
    recipients = None
    for i in range(len(args)):
        if args[i].startswith("-u"):
            recipients = args[i + 1].split(",")
            if not recipients:
                errors.append("Не указаны получатели (-u).")
            break
    if not recipients:
        errors.append("Отсутствует флаг '-u' для указания получателей.")

    # Проверка дней недели (-d)
    days = None
    for i in range(len(args)):
        if args[i].startswith("-d"):
            days = args[i + 1].split(",")
            valid_days = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"}
            invalid_days = [day for day in days if day not in valid_days]
            if invalid_days:
                errors.append(f"Некорректные дни недели: {', '.join(invalid_days)}")
            break
    if not days:
        errors.append("Отсутствует флаг '-d' для указания дней недели.")

    # Проверка времени (-t)
    time = None
    for i in range(len(args)):
        if args[i].startswith("-t"):
            time = args[i + 1]
            if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", time):
                errors.append(f"Неверный формат времени: {time}. Используйте HH:MM.")
            break
    if not time:
        errors.append("Отсутствует флаг '-t' для указания времени.")

    # Проверка сообщения (-m)
    message = None
    for i in range(len(args)):
        if args[i].startswith("-m"):
            message = " ".join(args[i + 1:]).strip()
            if not message:
                errors.append("Сообщение не может быть пустым (-m).")
            break
    if not message:
        errors.append("Отсутствует флаг '-m' для сообщения.")

    # Проверка окончания задачи (-e)
    end_time = None
    for i in range(len(args)):
        if args[i].startswith("-e"):
            try:
                end_time = datetime.strptime(args[i + 1], "%d-%m-%Y")
            except ValueError:
                errors.append(f"Некорректный формат даты окончания (-e): {args[i + 1]}. Используйте формат ДД-ММ-ГГГГ.")
            break

    return (False, errors) if errors else (True, "Команда корректна.")


def create_schedule(args, message):
    # Парсим аргументы (дни, время, получатели, сообщение)
    recipients, days, time, text_message = None, None, None, None
    message.text = re.sub(r'(@\w+),', r'\1 ', message.text)
    mentioned_participants, teams, mentioned_dogs = get_complete_mentions(message)
    recipients = ",".join([str(participant.id) for participant in mentioned_participants])
    recipients_dogs_ids = ",".join([str(participant.id) for participant in mentioned_dogs])
    if recipients_dogs_ids:
        recipients = recipients + "," + recipients_dogs_ids

    for i in range(len(args)):

        if args[i].startswith("-d"):
            days = args[i + 1]  # Получаем список дней
        elif args[i].startswith("-t"):
            time = args[i + 1]  # Получаем время отправки
        elif args[i].startswith("-m"):
            text_message = " ".join(args[i + 1:])  # Сообщение

    save_scheduled_task(recipients,
                        text_message,
                        message.chat.id,
                        message.message_thread_id if message.is_topic_message else None,
                        days,
                        time)


def cancel_schedule_service(schedule_id):
    return delete_scheduled_task(schedule_id)


def get_active_schedules_service():
    return get_active_schedules()


def get_all_schedules_service(chat_id):
    schedules = get_active_schedules_by_chat(chat_id)  # Получаем задачи из репозитория

    # Преобразуем задачи в удобный формат для отображения
    schedule_list = []
    for schedule in schedules:
        schedule_info = (
                            f"Айди: {schedule.id}, "
                            f"Сообщение: {schedule.message}, "
                            f"Получатели: {schedule.recipients}, "
                            f"Дни: {schedule.days}, "
                            f"Время: {schedule.time} "
                        ) + "\n"
        schedule_list.append(schedule_info)

    return schedule_list
