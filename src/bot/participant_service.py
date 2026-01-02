# participant_service.py
from telebot.formatting import escape_markdown
from utils import (
    create_mentions_text,
    send_data_not_found_message,
)

from common.repository import get_participants_by_group
from common.repository import toggle_vacation

def handle_vacation(message, bot):
    participant_id = message.from_user.id

    new_value = toggle_vacation(participant_id)

    if new_value is None:
        bot.reply_to(
            message,
            "Ой, похоже, тебя нет в базе участников 😿",
            parse_mode="MarkdownV2"
        )
        return

    status_text = "в отпуске 🏖️" if new_value else "снова на связи 💪"

    bot.reply_to(
        message,
        escape_markdown(f"Готово! Теперь ты {status_text}"),
        parse_mode="MarkdownV2",
    )

def handle_all_command(message, bot):
    group_id = message.chat.id

    participants = get_participants_by_group(group_id)

    if not participants:
        send_data_not_found_message(
            message,
            "Ой, похоже, у меня ещё нет данных об участниках. Попробуйте команду на обновление.",
            bot,
        )
        return

    reply_message = create_mentions_text(participants=participants)

    # Отправляем ответ с упоминаниями
    bot.reply_to(message, reply_message, parse_mode="MarkdownV2")
