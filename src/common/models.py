from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)

    # Связь с участниками через таблицу ParticipantGroup
    participant_associations = relationship("ParticipantGroup", back_populates="group")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    # Связь с группами через таблицу ParticipantGroup
    group_associations = relationship("ParticipantGroup", back_populates="participant")
    # Связь с TeamParticipant
    team_associations = relationship("TeamParticipant", back_populates="participant")

    def __init__(self, id, username=None, first_name=None, last_name=None):
        self.id = id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )


class ParticipantGroup(Base):
    __tablename__ = "participant_groups"

    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("participant_id", "group_id"),)

    participant = relationship("Participant", back_populates="group_associations")
    group = relationship("Group", back_populates="participant_associations")


class TeamParticipant(Base):
    __tablename__ = "team_participants"

    team_name = Column(String, nullable=False)
    group_id = Column(Integer, nullable=False)
    participant_id = Column(Integer, ForeignKey("participants.id"), nullable=False)

    __table_args__ = (PrimaryKeyConstraint("team_name", "group_id", "participant_id"),)

    # Связь с участником
    participant = relationship("Participant", back_populates="team_associations")
