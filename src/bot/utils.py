# utils.py
from telebot.formatting import escape_markdown


def check_bot_delete_permissions(group_id, bot):
    bot_member = bot.get_chat_member(group_id, bot.get_me().id)
    return bot_member.can_delete_messages


# Метод не используется, но сохранён на всякий случай
def send_permission_error_message(group_id, bot):
    bot.send_message(
        chat_id=group_id,
        text="У меня нет нужных прав для выполнения этой команды. "
        "Пожалуйста, предоставьте нужные права администратора",
    )


def create_mentions_text(participants, message_text, author_name):
    active_participants = [
        p for p in participants if not getattr(p, "vacation", False)
    ]

    mentions = ", ".join(
        f"[{escape_markdown(p.first_name or '')} {escape_markdown(p.last_name or '')}](tg://user?id={p.id})"
        for p in active_participants
    )

    return (
        f"{escape_markdown(author_name)} написал:\n"
        f"{escape_markdown(message_text or '')}\n"
        f"{mentions}"
    )

# def create_mentions_text(participants):
#     return create_mentions_text("Обратите внимание", participants)

def create_mentions_text(participants, init_text="Обратите внимание"):
    active_participants = [
        p for p in participants if not getattr(p, "vacation", False)
    ]

    mentions = ", ".join(
        f"[{escape_markdown(p.first_name or '')} {escape_markdown(p.last_name or '')}](tg://user?id={p.id})"
        for p in active_participants
    )
    return f"{escape_markdown(init_text or '')}, {mentions}"


def send_data_not_found_message(message, text, bot):
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        message_thread_id=(
            message.message_thread_id if message.is_topic_message else None
        ),
    )
