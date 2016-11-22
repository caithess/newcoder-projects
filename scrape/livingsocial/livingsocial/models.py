from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import livingsocial.settings as settings

DeclarativeBase = declarative_base()


def db_connect():
    '''Connects with settings.py to Postgres. Returns sqlalchemy obj.'''
    return create_engine(URL(**settings.DATABASE))


def create_tables(engine):
    DeclarativeBase.metadata.create_all(engine)


class Deal(DeclarativeBase):
    '''SQlalchemy Postgres livingsocial_deals model'''
    __tablename__ = 'livingsocial_deals'
    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    subtitle = Column('subtitle', String, nullable=True)
    description = Column('description', String, nullable=True)
    link = Column('link', String, nullable=True)
    location = Column('location', String, nullable=True)
    original_price = Column('original_price', Integer, nullable=True)
    price = Column('price', Integer, nullable=True)
