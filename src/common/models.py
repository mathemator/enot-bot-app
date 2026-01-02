from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, ARRAY, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    vacation = Column(Boolean, nullable=False, default=False)

    # Связь с группами через таблицу ParticipantGroup
    group_associations = relationship("ParticipantGroup", back_populates="participant")
    # Связь с TeamParticipant
    team_associations = relationship("TeamParticipant", back_populates="participant")

    def __init__(self, id, username=None, first_name=None, last_name=None, vacation=False):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.vacation = vacation

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "vacation": self.vacation,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            vacation=data.get("vacation", False),
        )


class ParticipantGroup(Base):
    __tablename__ = "participant_groups"

    participant_id = Column(
        Integer,
        ForeignKey("participants.id", name="fk_participant_groups_participant_id"),
        nullable=False,
    )
    group_id = Column(Integer, nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint(
            "participant_id", "group_id", name="pk_participant_groups"
        ),
    )

    participant = relationship("Participant", back_populates="group_associations")


class TeamParticipant(Base):
    __tablename__ = "team_participants"

    team_name = Column(String, nullable=False)
    group_id = Column(Integer, nullable=False)
    participant_id = Column(
        Integer,
        ForeignKey("participants.id", name="fk_team_participants_participant_id"),
        nullable=False,
    )

    __table_args__ = (
        PrimaryKeyConstraint(
            "team_name", "group_id", "participant_id", name="team_participants"
        ),
    )

    # Связь с участником
    participant = relationship("Participant", back_populates="team_associations")


# ================== ШЕДУЛЕРЫ =====================
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    chat_id = Column(Integer, nullable=False)  # Идентификатор чата
    thread_id  = Column(Integer, nullable=True)  # Идентификатор темы подчата опционально
    recipients = Column(String, nullable=False)  # Список получателей
    days = Column(String, nullable=False)  # Список дней
    time = Column(String, nullable=False)  # Время отправки

    def __init__(self, message, chat_id, thread_id, recipients, days, time):
        self.message = message
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.recipients = recipients
        self.days = days
        self.time = time

    def get_recipients_list(self):
        return self.recipients.split(',')  # Преобразуем строку обратно в список

    def get_scheduled_days_list(self):
        return self.days.split(',')  # Преобразуем строку обратно в список
