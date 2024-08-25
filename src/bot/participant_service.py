# participant_service.py
from telebot.formatting import escape_markdown
from utils import (
    check_bot_delete_permissions,
    create_mentions_text,
    send_data_not_found_message,
    send_permission_error_message,
)

from common.repository import get_participants_by_group


def handle_all_command(message, bot):
    group_id = message.chat.id

    if not check_bot_delete_permissions(group_id, bot):
        send_permission_error_message(group_id, bot)
        return

    participants = get_participants_by_group(group_id)

    if not participants:
        send_data_not_found_message(
            message,
            "Ой, похоже, у меня ещё нет данных об участниках. Попробуйте команду на обновление.",
            bot,
        )
        return

    bot_id = bot.get_me().id
    message_text = (
        message.text.split(maxsplit=1)[1]
        if len(message.text.split(maxsplit=1)) > 1
        else ""
    )
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
