# team_service.py
import re
from utils import (
    check_bot_delete_permissions,
    create_mentions_text,
    send_data_not_found_message
)

from common.repository import (
    delete_team,
    get_existing_team_members,
    get_participants_by_group,
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
            bot.reply_to(message, f"Ошибка: имя '{team_name}' уже занято участником {participant.username}.")
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

    # Регулярное выражение для поиска MarkdownV2 упоминаний
    markdown_mention_pattern = re.compile(r'\[(.*?)\]\(tg://user\?id=(\d+)\)')

    # Разбиваем сообщение на части
    parts = message.text.split()

    # Списки для хранения упомянутых команд, пользователей и текста
    teams_or_usernames = []
    user_mentions = []
    user_ids = []
    text_parts = []

    participants = get_participants_by_group(message.chat.id)

    # Определяем команды, пользователей и текст
    for part in parts:
        if part.startswith('@'):
            # Если часть начинается с @, это команда или пользователь
            username_or_team = part[1:]
            if any(
                    participant.username and participant.username.lower() == username_or_team.lower()
                    for participant in participants
            ):
                user_mentions.append(username_or_team)
            else:
                teams_or_usernames.append(username_or_team)
        else:
            # Ищем упоминания пользователей в формате MarkdownV2
            markdown_mentions = markdown_mention_pattern.findall(part)
            if markdown_mentions:
                for mention in markdown_mentions:
                    user_id = int(mention[1])
                    user_ids.append(user_id)
            else:
                # Обычный текст
                text_parts.append(part)

    # Получаем все команды группы
    teams = get_teams_by_group(message.chat.id)
    valid_teams = [team for team in teams_or_usernames if team in teams]

    # Получаем участников всех команд
    all_team_member_ids = set()
    for team_name in valid_teams:
        team_member_ids = get_existing_team_members(team_name, message.chat.id)
        all_team_member_ids.update(team_member_ids)

    # Формируем список участников для упоминания
    mentioned_participants = [
        p for p in participants
        if p.id in all_team_member_ids or p.username in user_mentions or p.id in user_ids
    ]

    # Убираем из упоминаний автора сообщения
    mentioned_participants = [p for p in mentioned_participants if p.id != message.from_user.id]

    if mentioned_participants:
        bot_id = bot.get_me().id
        author_name = (
            f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
        )
        message_text = " ".join(text_parts).strip()
        full_message = create_mentions_text(
            mentioned_participants, bot_id, message_text, author_name
        )

        bot.send_message(
            chat_id=message.chat.id,
            text=full_message,
            parse_mode="MarkdownV2",
            message_thread_id=(
                message.message_thread_id if message.is_topic_message else None
            ),
        )

        if check_bot_delete_permissions(group_id, bot):
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        bot.reply_to(
            message,
            "Не удалось найти участников упомянутых команд или пользователей.",
        )


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
