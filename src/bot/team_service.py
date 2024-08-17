# team_service.py
from telebot.formatting import escape_markdown

from utils import (
    check_bot_permissions,
    create_mentions_text,
    send_data_not_found_message,
    send_permission_error_message,
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
    # Извлечение команды из сообщения
    command_or_username = message.text.split()[0][1:]  # Убираем символ '@'

    print(command_or_username)
    # Проверяем, есть ли участник с таким username в чате
    participants = get_participants_by_group(message.chat.id)
    for participant in participants:
        if (
            participant.username
            and participant.username.lower() == command_or_username.lower()
        ):
            # Если такой участник найден, бот ничего не делает
            return

    # Проверка, существует ли команда с таким именем
    teams = get_teams_by_group(message.chat.id)
    print(teams)
    print(command_or_username in teams)
    if command_or_username in teams:
        message.text = f"/team {command_or_username} {message.text[len(command_or_username) + 2:]}"  # Формируем команду как /team название
        handle_team(message, bot)  # Вызываем обработчик команды /team
    else:
        bot.reply_to(
            message,
            f"Команда или участник с именем '{command_or_username}' не найдены.",
        )


def handle_team(message, bot):
    group_id = message.chat.id

    if not check_bot_permissions(group_id, bot):
        send_permission_error_message(group_id, bot)
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        send_data_not_found_message(
            message, "Пожалуйста, укажите название команды и текст сообщения.", bot
        )
        return

    team_name = parts[1].split(maxsplit=1)[0]
    message_text = parts[1][len(team_name) :].strip()
    team_member_ids = get_existing_team_members(team_name, group_id)
    participants = [
        p for p in get_participants_by_group(group_id) if p.id in team_member_ids
    ]

    if not participants:
        send_data_not_found_message(
            message,
            f'Ой, похоже, у меня нет данных об участниках команды "{team_name}".',
            bot,
        )
        return

    bot_id = bot.get_me().id
    author_name = (
        f"{message.from_user.first_name} {message.from_user.last_name or ''}".strip()
    )
    message_text = message_text
    full_message = create_mentions_text(participants, bot_id, message_text, author_name)

    bot.send_message(
        chat_id=message.chat.id,
        text=full_message,
        parse_mode="MarkdownV2",
        message_thread_id=(
            message.message_thread_id if message.is_topic_message else None
        ),
    )

    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


def handle_teams(message, bot):
    group_id = message.chat.id

    if not check_bot_permissions(group_id, bot):
        send_permission_error_message(group_id, bot)
        return

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
