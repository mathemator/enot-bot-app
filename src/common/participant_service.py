import os
import logging
from sqlalchemy import create_engine, Column, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from common.models import Participant, Base

# Определение базовой директории проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'database.db')

# Создание директории, если она не существует
os.makedirs(DATA_DIR, exist_ok=True)

# URL базы данных SQLite
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'database.db')}"

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
        for user in participants:
            # Проверяем, существует ли уже участник с таким id
            existing_participant = db.query(Participant).filter_by(id=user.id, group_id=group_id).first()

            if existing_participant:
                # Если участник существует, обновляем его данные
                existing_participant.first_name = user.first_name
                existing_participant.last_name = user.last_name
                existing_participant.group_id = group_id
            else:
                # Если участник не существует, создаем новый
                participant = Participant(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    group_id=group_id
                )
                db.add(participant)

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
        # Извлекаем все записи для указанной группы
        participants = db.query(Participant).filter_by(group_id=group_id).all()
        return participants  # Возвращаем список объектов Participant
    except Exception as e:
        print(f"Error retrieving participants: {e}")
        return []
    finally:
        db.close()