import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


DB_URL = 'full.db'
engine = create_engine('sqlite:///' + DB_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)()


class Word(Base):
    __tablename__ = 'words'

    word = Column(String, primary_key=True)
    audios = relationship('Audio')


class Audio(Base):
    __tablename__ = 'audios'
    id = Column(Integer, primary_key=True)
    word = Column(String, ForeignKey('words.word'))
    audio_file = Column(String)
    start = Column(Float)
    end = Column(Float)
    speaker_id = Column(Integer)


# Initialize database if it doesn't exist
if not os.path.exists(DB_URL):
    Base.metadata.create_all(engine)
