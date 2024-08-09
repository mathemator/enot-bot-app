import json

FILENAME_TEMPLATE = 'participants-{group_id}.json'

# Функция для сохранения списка участников в JSON-файл
def save_participants(participants, group_id):
    filename = FILENAME_TEMPLATE.format(group_id=group_id)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump([user.to_dict() for user in participants], f, ensure_ascii=False, indent=4)
    return filename