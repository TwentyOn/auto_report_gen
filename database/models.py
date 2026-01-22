from sqlalchemy import select, Column, Integer, String, Boolean, ForeignKey, and_

from database.db import Base, session_maker
from settings import DB_SCHEME


class Report(Base):
    __tablename__ = 'report'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    product_id = Column(Integer, ForeignKey(f'{DB_SCHEME}.product.id', ondelete='RESTRICT'))
    status_id = Column(Integer)
    filepath = Column(String)
    to_delete = Column(Boolean)
    content_report_filepath = Column(String)

    # product = relationship('Product', uselist=False, backref='reports')


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String)


# отладка
if __name__ == '__main__':
    with session_maker() as session:
        a = session.execute(
            select(Report.id, Product.name).join(Product, Report.product_id == Product.id).where(Report.id == 114))
        print(a.all())
