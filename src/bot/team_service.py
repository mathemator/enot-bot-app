# team_service.py

from utils import (
    check_bot_delete_permissions,
    create_mentions_text,
    send_data_not_found_message,
)

from common.repository import (
    delete_team,
    get_existing_team_members,
    get_participants_by_group,
    get_participants_by_usernames,
    get_teams_by_group,
    save_team,
)


def handle_team_set(message, bot):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите имя команды и участников.")
        return

    team_name = command_parts[1]

    # Получаем список участников в чате
    participants = get_participants_by_group(message.chat.id)

    # Проверяем, существует ли участник с таким именем, как имя команды
    for participant in participants:
        if participant.username and participant.username.lower() == team_name.lower():
            bot.reply_to(
                message,
                f"Ошибка: имя '{team_name}' уже занято участником {participant.username}.",
            )
            return

    usernames = []
    user_ids = []

    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[
                    entity.offset + 1 : entity.offset + entity.length
                ]
                usernames.append(username)
            elif entity.type == "text_mention":
                user_id = entity.user.id
                user_ids.append(user_id)

    if not usernames and not user_ids:
        bot.reply_to(message, "Пожалуйста, упомяните хотя бы одного участника команды.")
        return

    chat_id = message.chat.id
    try:
        save_team(chat_id, team_name, usernames, user_ids)
        bot.reply_to(message, f"Команда '{team_name}' успешно сохранена!")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при сохранении команды: {e}")


def handle_team_mention(message, bot):
    group_id = message.chat.id

    # Списки для хранения упомянутых команд и текста
    teams_or_usernames = []
    text_parts = []
    mentioned_participants = []  # Для хранения всех участников, которые будут упомянуты

    message_text = (
        message.text if message.text else message.caption
    )  # Исходный текст сообщения

    # Получаем команды, которые существуют в группе
    group_teams = get_teams_by_group(group_id)

    # Получаем участников в чате
    participants = get_participants_by_group(group_id)

    # Обрабатываем entities для поиска упоминаний без @
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention":
                # Упоминание через MarkdownV2 [username](tg://user?id=...)
                user_id = entity.user.id
                participant = next((p for p in participants if p.id == user_id), None)
                if participant:
                    mentioned_participants.append(participant)

    # Обрабатываем текст, чтобы выделить команды и текст сообщения
    parts = message_text.split()
    for part in parts:
        if part.startswith("@"):
            username_or_team = part[1:]
            # Проверяем, является ли это упоминанием команды
            if username_or_team in group_teams:
                teams_or_usernames.append(username_or_team)
                # Удаляем упоминание команды из текста
                start = message_text.find(part)
                end = start + len(part)
                message_text = message_text[:start] + message_text[end:]
            else:
                text_parts.append(part)
        else:
            text_parts.append(part)

    # Получаем команды, которые существуют
    teams = group_teams
    valid_teams = [team for team in teams_or_usernames if team in teams]

    # Получаем участников всех команд
    all_teams_member_ids = set()
    for team_name in valid_teams:
        team_member_ids = get_existing_team_members(team_name, message.chat.id)
        all_teams_member_ids.update(team_member_ids)

    # Получаем участников в чате
    participants = get_participants_by_group(message.chat.id)

    # Формируем список участников для упоминания
    for p in participants:
        if p.id in all_teams_member_ids:
            mentioned_participants.append(p)

    # Убираем из упоминаний автора сообщения и бота
    mentioned_participants = [
        p
        for p in mentioned_participants
        if (p.id != message.from_user.id and p.id != bot.get_me().id)
    ]

    if mentioned_participants and teams_or_usernames:
        reply_message = create_mentions_text(mentioned_participants)

        # Отправляем ответ с упоминаниями
        bot.reply_to(message, reply_message, parse_mode="MarkdownV2")


def handle_teams(message, bot):
    group_id = message.chat.id

    teams = get_teams_by_group(group_id)

    if not teams:
        send_data_not_found_message(
            message, "Ой, похоже, у меня нет данных о командах в этой группе.", bot
        )
        return

    team_details = []
    for team in teams:
        # Получаем участников команды
        team_member_ids = get_existing_team_members(team, group_id)
        participants = [
            p for p in get_participants_by_group(group_id) if p.id in team_member_ids
        ]

        # Создаем список участников
        participant_names = ", ".join(
            f"{p.first_name} {p.last_name or ''}".strip() for p in participants
        )

        # Добавляем команду и её участников в список
        team_details.append(f"• {team}: {participant_names}")

    # Объединяем все команды и участников в одну строку
    team_details_text = "\n".join(team_details)

    bot.send_message(
        chat_id=message.chat.id,
        text=f"Вот список команд в этой группе:\n{team_details_text}",
        message_thread_id=(
            message.message_thread_id if message.is_topic_message else None
        ),
    )


def handle_team_delete(message, bot):
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите имя команды для удаления.")
        return

    team_name = command_parts[1].strip()

    chat_id = message.chat.id
    try:
        delete_team(chat_id, team_name)
        bot.reply_to(message, f"Команда '{team_name}' успешно удалена!")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка при удалении команды: {e}")


def handle_invite_team_participants(message, bot):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите имя команды и участников.")
        return

    team_name = command_parts[1]

    # Проверяем, существует ли команда с таким именем
    chat_id = message.chat.id
    teams = get_teams_by_group(chat_id)
    if team_name not in teams:
        bot.reply_to(message, f"Команда '{team_name}' не найдена.")
        return

    # Списки для хранения упомянутых пользователей
    usernames = []
    user_ids = []

    # Извлекаем упоминания из entities
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[
                    entity.offset + 1 : entity.offset + entity.length
                ]
                usernames.append(username)
            elif entity.type == "text_mention":
                user_id = entity.user.id
                user_ids.append(user_id)

    resolved_ids = list(get_participants_by_usernames(usernames).values())
    user_ids.extend(resolved_ids)

    # Добавляем упомянутых участников в команду
    if usernames or user_ids:
        try:
            invite_participants_to_team(chat_id, team_name, user_ids)
            bot.reply_to(
                message, f"Участники успешно добавлены в команду '{team_name}'."
            )
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка при добавлении участников: {e}")
    else:
        bot.reply_to(message, "Пожалуйста, укажите хотя бы одного участника.")


# Функция для добавления участников в команду
def invite_participants_to_team(chat_id, team_name, user_ids):
    # Получаем текущих участников команды
    current_member_ids = get_existing_team_members(team_name, chat_id)
    for user_id in user_ids:
        if user_id not in current_member_ids:
            current_member_ids.add(user_id)

    # Сохраняем обновленный список участников команды
    save_team(chat_id, team_name, [], current_member_ids)


def handle_team_kick(message, bot):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        bot.reply_to(message, "Пожалуйста, укажите имя команды и участников.")
        return

    team_name = command_parts[1]

    # Проверяем, существует ли команда с таким именем
    chat_id = message.chat.id
    teams = get_teams_by_group(chat_id)
    if team_name not in teams:
        bot.reply_to(message, f"Команда '{team_name}' не найдена.")
        return

    # Списки для хранения упомянутых пользователей
    usernames = []
    user_ids = []

    # Извлекаем упоминания из entities
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                username = message.text[
                    entity.offset + 1 : entity.offset + entity.length
                ]
                usernames.append(username)
            elif entity.type == "text_mention":
                user_id = entity.user.id
                user_ids.append(user_id)

    resolved_ids = [
        participant.id for participant in get_participants_by_usernames(usernames)
    ]
    user_ids.extend(resolved_ids)

    # Удаляем указанных участников из команды
    if usernames or user_ids:
        try:
            remove_participants_from_team(chat_id, team_name, user_ids)
            bot.reply_to(
                message, f"Участники успешно удалены из команды '{team_name}'."
            )
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка при удалении участников: {e}")
    else:
        bot.reply_to(message, "Пожалуйста, укажите хотя бы одного участника.")


# Функция для удаления участников из команды
def remove_participants_from_team(chat_id, team_name, user_ids):
    # Получаем текущих участников команды
    current_member_ids = get_existing_team_members(team_name, chat_id)

    # Создаем список для обновленных участников команды
    updated_member_ids = current_member_ids.copy()

    for user_id in user_ids:
        if user_id in updated_member_ids:
            updated_member_ids.remove(user_id)

    # Сохраняем обновленный список участников команды
    save_team(chat_id, team_name, [], updated_member_ids)
