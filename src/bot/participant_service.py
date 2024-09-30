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

    reply_message = create_mentions_text(participants)

    # Отправляем ответ с упоминаниями
    bot.reply_to(message, reply_message, parse_mode="MarkdownV2")
