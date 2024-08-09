from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, PrimaryKeyConstraint

Base = declarative_base()

class Participant(Base):
    __tablename__ = 'participants'

    id = Column(Integer, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    group_id = Column(Integer, nullable=False)

    # Составной первичный ключ
    __table_args__ = (
        PrimaryKeyConstraint('id', 'group_id'),
    )

    def __init__(self, id, first_name, last_name, group_id=None):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.group_id = group_id

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'group_id': self.group_id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['id'],
            data.get('first_name'),
            data.get('last_name'),
            data.get('group_id')
        )