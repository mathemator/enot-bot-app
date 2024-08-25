import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from common.models import Base, Participant, ParticipantGroup, TeamParticipant

# Определение базовой директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/database.db")
DATA_DIR = os.path.dirname(DATABASE_PATH)

# Создание директории, если она не существует
os.makedirs(DATA_DIR, exist_ok=True)

# URL базы данных SQLite
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание локальной сессии
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


# Функция для сохранения участников в базу данных
def save_participants(participants, group_id):
    db = SessionLocal()
    try:
        # Получаем текущий список участников в группе
        current_participants = (
            db.query(ParticipantGroup).filter_by(group_id=group_id).all()
        )

        # Получаем список ID участников, которые остались в группе
        participants_ids = {user.id for user in participants}

        # Удаляем участников, которых больше нет в группе
        for current_participant in current_participants:
            if current_participant.participant_id not in participants_ids:
                # Удаляем связь участника с группой
                db.delete(current_participant)

                # Также удаляем связь участника с командой, если это требуется
                db.query(TeamParticipant).filter_by(
                    participant_id=current_participant.participant_id
                ).delete()

        for user in participants:
            existing_participant = db.query(Participant).filter_by(id=user.id).first()

            if existing_participant:
                existing_participant.username = user.username
                existing_participant.first_name = user.first_name
                existing_participant.last_name = user.last_name
            else:
                participant = Participant(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                )
                db.add(participant)

            existing_participant_group = (
                db.query(ParticipantGroup)
                .filter_by(participant_id=user.id, group_id=group_id)
                .first()
            )

            if not existing_participant_group:
                participant_group = ParticipantGroup(
                    participant_id=user.id, group_id=group_id
                )
                db.add(participant_group)

        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving participants: {e}")
        raise e
    finally:
        db.close()


def get_participants_by_group(group_id):
    db = SessionLocal()
    try:
        # Извлекаем все записи для указанной группы через таблицу ParticipantGroup
        participant_ids = (
            db.query(ParticipantGroup.participant_id).filter_by(group_id=group_id).all()
        )
        participant_ids = [
            id for (id,) in participant_ids
        ]  # Преобразуем список к обычному списку идентификаторов

        # Извлекаем участников по идентификаторам
        participants = (
            db.query(Participant).filter(Participant.id.in_(participant_ids)).all()
        )
        return participants  # Возвращаем список объектов Participant
    except Exception as e:
        print(f"Error retrieving participants: {e}")
        return []
    finally:
        db.close()


def get_participants_by_usernames(usernames):
    db = SessionLocal()
    try:
        participants = (
            db.query(Participant).filter(Participant.username.in_(usernames)).all()
        )
        return {participant.username: participant.id for participant in participants}
    except Exception as e:
        print(f"Error retrieving participants by usernames: {e}")
        return {}
    finally:
        db.close()


def get_existing_team_members(team_name, group_id):
    db = SessionLocal()
    try:
        # Получение текущих участников команды
        participants = (
            db.query(TeamParticipant)
            .filter_by(team_name=team_name, group_id=group_id)
            .all()
        )
        return {participant.participant_id for participant in participants}
    except Exception as e:
        print(f"Error retrieving team participants: {e}")
        return set()
    finally:
        db.close()


def get_teams_by_group(group_id):
    db = SessionLocal()
    try:
        # Извлечение всех уникальных команд для указанной группы
        print(db.query(TeamParticipant.team_name).all())
        teams = (
            db.query(TeamParticipant.team_name)
            .filter_by(group_id=group_id)
            .distinct()
            .all()
        )
        return [team.team_name for team in teams]  # Возвращаем список имен команд
    except Exception as e:
        print(f"Error retrieving teams: {e}")
        return []
    finally:
        db.close()


def save_team(group_id, team_name, usernames, user_ids):
    db = SessionLocal()
    try:
        # Удаление всех текущих участников команды
        db.query(TeamParticipant).filter_by(
            team_name=team_name, group_id=group_id
        ).delete()

        # Получение идентификаторов пользователей по username
        username_to_id = get_participants_by_usernames(usernames)

        # Объединяем идентификаторы из username_to_id и user_ids
        all_user_ids = set(user_ids).union(set(username_to_id.values()))

        # Добавление новых участников команды
        for user_id in all_user_ids:
            team_participant = TeamParticipant(
                team_name=team_name,  # У нас больше нет поля `chat_id` в TeamParticipant
                group_id=group_id,  # Используем group_id для идентификации группы
                participant_id=user_id,
            )
            db.add(team_participant)

        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error saving team: {e}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()


def delete_team(chat_id, team_name):
    db = SessionLocal()
    try:
        # Удаляем все участники команды
        db.query(TeamParticipant).filter_by(
            group_id=chat_id, team_name=team_name
        ).delete()

        db.commit()
    except IntegrityError as e:
        db.rollback()
        print(f"Error removing team: {e}")
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
    finally:
        db.close()


# прозапас
def delete_participant_if_unlinked(db, participant_id):
    """
    Удаляет участника из базы данных, если он больше не привязан ни к одной группе или команде.

    :param db: Текущая сессия базы данных.
    :param participant_id: ID участника, которого нужно проверить.
    """
    related_group_count = (
        db.query(ParticipantGroup).filter_by(participant_id=participant_id).count()
    )
    related_team_count = (
        db.query(TeamParticipant).filter_by(participant_id=participant_id).count()
    )

    if related_group_count == 0 and related_team_count == 0:
        participant_to_delete = (
            db.query(Participant).filter_by(id=participant_id).first()
        )
        if participant_to_delete:
            db.delete(participant_to_delete)
