import argparse

import pandas as pd
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship

from config import db_path

def db_engine(path = db_path):
    return create_engine('sqlite:///%s' % path, echo=False)

class DbSession(object):
    engine = db_engine(db_path)
    def __enter__(self):
        session = sessionmaker()
        session.configure(bind=self.engine)
        self.session = session()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

Base = declarative_base()

class AccountsMixin(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    type = Column(String)
    description = Column(String)
    value = Column(Float)
    balance = Column(Float)
    account_name = Column(String)
    account_number = Column(String)

class Debit(AccountsMixin, Base):
    pass

class Credit(AccountsMixin, Base):
    pass

class Isa(AccountsMixin, Base):
    pass

class Bills(AccountsMixin, Base):
    pass

class Transactions(AccountsMixin, Base):
    classified = relationship('Classified')

class Classified(Base):
    __tablename__ = 'classified'
    id = Column(Integer, primary_key=True)
    transactions_id = Column(Integer, ForeignKey('transactions.id'))
    category = Column(String, ForeignKey('category.level_one'))

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer)
    classified = relationship('Classified')
    level_one = Column(String, primary_key=True)
    level_two = Column(String)
    level_three = Column(String)

class Budget(Base):
    __tablename__ = 'budget'
    id = Column(Integer, primary_key=True)
    category = Column(String, ForeignKey('category.level_one'))
    monthly = Column(Float)
    yearly = Column(Float)

class Income(Base):
    __tablename__ = 'income'
    name = Column(String, primary_key=True)
    monthly = Column(Float)

def categories_from_csv(engine, file_name):
    df = pd.read_csv(file_name, encoding='utf-8')
    df.to_sql(con=engine, index_label='id', name=Category.__tablename__, if_exists='replace')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--categories", help="add categories to db from given csv file")
    args = parser.parse_args()
    engine = db_engine()
    Base.metadata.create_all(engine, checkfirst=True)
    if args.categories:
        file_name = 'categories.csv'
        categories_from_csv(engine, file_name)
