from sqlalchemy import select, Column, Integer, String, Boolean, and_

from database.db import Base, session_maker
from settings import DB_SCHEME


class Report(Base):
    __tablename__ = 'report'
    __table_args__ = {'schema': DB_SCHEME}

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    status_id = Column(Integer)
    filepath = Column(String)
    to_delete = Column(Boolean)


with session_maker() as session:
    a = session.execute(select(Report.id).where(and_(Report.status_id == 2, Report.to_delete == False)))
    print(a.scalars().all())
