from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from settings import DB_USER, DB_NAME, DB_PORT, DB_HOST, DB_PASSWORD, DB_SCHEME

DATABASE_URL = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class Base(DeclarativeBase):
    __table_args__ = {'schema': DB_SCHEME}


engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=engine)